#!/usr/bin/env python3
"""
Mem0 共享记忆 MCP Server — 多 Agent 共享经验（retain/recall/delete/list）
- LLM: DeepSeek API（提取/总结）
- Embedder: bge-m3 本地（CPU，不占 GPU）
- 存储: Qdrant 本地（~/.mem0 或 .mem0/qdrant）
用法: 由 pi / Codex 等 MCP 客户端通过 stdio 拉起（见 .mcp.json）
"""
import os
import sys

# ⚠️ 环境变量必须在 import mem0/sentence-transformers 之前设置（它们 import 时读配置）
# 强制离线：bge-m3 已缓存在 ~/.cache/huggingface（4.3G），启动无需联网
os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("HF_ENDPOINT", "https://hf-mirror.com")
os.environ.setdefault("MEM0_TELEMETRY", "false")

# 运行环境: mem0 conda env（确保 mem0 已安装）
try:
    from mem0 import Memory
except ImportError:
    sys.exit("mem0 not installed. Run: pip install mem0ai 'mem0ai[nlp]' sentence-transformers")

MEM0_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".mem0")


def _get_api_key() -> str:
    """key 读取顺序：环境变量 → ~/.config/mem0_deepseek_key 文件（600 权限，不入 git）"""
    key = os.environ.get("MEM0_DEEPSEEK_API_KEY") or os.environ.get("DEEPSEEK_API_KEY")
    if key:
        return key
    keyfile = os.path.expanduser("~/.config/mem0_deepseek_key")
    if os.path.exists(keyfile):
        with open(keyfile) as f:
            return f.read().strip()
    return ""

CONFIG = {
    "llm": {
        "provider": "deepseek",
        "config": {
            "api_key": _get_api_key(),
            "model": "deepseek-chat",
        },
    },
    "embedder": {
        "provider": "huggingface",
        "config": {
            "model": "BAAI/bge-m3",
            # sentence-transformers 默认探测 CUDA 后会把 bge-m3 放 GPU（实测占 2.6GB 显存）；
            # 强制 CPU 推理，释放显存给生视频用。代价：embedding 稍慢（毫秒~百毫秒级，可忽略）
            "model_kwargs": {"device": "cpu"},
        },
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "path": os.path.join(MEM0_DIR, "qdrant"),
            "embedding_model_dims": 1024,  # bge-m3 维度（QdrantConfig 默认 1536 是 OpenAI 的，必须覆盖）
        },
    },
    "history_db_path": os.path.join(MEM0_DIR, "history.db"),
    "custom_instructions": "记忆条目必须使用简体中文输出，保留关键技术术语（如 res_multistep、cfg、LoRA）原文。",
}

if not CONFIG["llm"]["config"]["api_key"]:
    sys.exit("No DeepSeek API key (set MEM0_DEEPSEEK_API_KEY / DEEPSEEK_API_KEY / ~/.config/mem0_deepseek_key)")

_memory = Memory.from_config(CONFIG)

from mcp.server.fastmcp import FastMCP

# HTTP 模式（streamable-http）：一个常驻实例服务所有 pi 会话，消除 stdio 多进程撞锁
mcp = FastMCP("mem0", host="127.0.0.1", port=8899)

PROJECT_USER = "comfy-ops"  # 项目级共享记忆池


def _filters(user_id: str = "", agent_id: str = ""):
    f = {"user_id": user_id or PROJECT_USER}
    if agent_id:
        f["agent_id"] = agent_id
    return f


@mcp.tool()
def memory_retain(content: str, user_id: str = "", agent_id: str = "") -> str:
    """存一条经验/事实到共享记忆库。内容用自然语言描述（如"Bernini 图像编辑用 res_multistep 采样器，LoRA 3.0/1.5"）。
    user_id 默认 comfy-ops（项目共享池）；agent_id 可选（区分来源 agent）。"""
    try:
        r = _memory.add(content, **_filters(user_id, agent_id))
        mems = [x.get("memory", "") for x in r.get("results", [])]
        return f"OK stored: {mems}"
    except Exception as e:
        return f"ERROR: {e}"


@mcp.tool()
def memory_recall(query: str, user_id: str = "", agent_id: str = "", limit: int = 5) -> list:
    """按语义检索共享记忆（如"Bernini 用什么采样器""之前测过超分多快"）。返回带相关度分数的记忆列表。"""
    try:
        r = _memory.search(query, filters=_filters(user_id, agent_id), limit=limit)
        return [
            {"score": round(x.get("score", 0), 3), "memory": x.get("memory", "")}
            for x in r.get("results", [])
        ]
    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
def memory_list(user_id: str = "", agent_id: str = "") -> list:
    """列出共享记忆库的全部记忆（用于审查/人工可读）。"""
    try:
        r = _memory.get_all(filters=_filters(user_id, agent_id))
        return [{"id": x.get("id", ""), "memory": x.get("memory", "")} for x in r.get("results", [])]
    except Exception as e:
        return [{"error": str(e)}]


@mcp.tool()
def memory_delete(memory_id: str) -> str:
    """删除一条记忆（先 memory_list 查 id；memory_id 全局唯一）。"""
    try:
        r = _memory.delete(memory_id)
        return f"deleted: {r}"
    except Exception as e:
        return f"ERROR: {e}"


@mcp.tool()
def memory_update(memory_id: str, content: str, user_id: str = "") -> str:
    """修改一条已有记忆的内容（memory_id 来自 memory_list）。
    
    注意：mem0 库 update() 不支持 user_id 参数（user_id/agent_id 创建后不可变），
    该参数仅保留在签名里兼容调用方，实际不传递。
    """
    try:
        r = _memory.update(memory_id, content)
        return f"updated: {r}"
    except Exception as e:
        return f"ERROR: {e}"


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
