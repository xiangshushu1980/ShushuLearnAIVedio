#!/bin/bash
# 跳板：mem0 已全局化（2025-08-02），真实脚本在 ~/.pi/agent/mem0/mem0.sh
# 保留此文件仅为兼容旧习惯调用，可直接用全局脚本。
exec ~/.pi/agent/mem0/mem0.sh "$@"
