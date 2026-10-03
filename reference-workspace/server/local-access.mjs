// Owner: Sean — existing loopback Host and same-origin mutation boundary.
import { HttpError } from './store.mjs';
export function localAccess(req, _res, next) {
  if (!/^(127\.0\.0\.1|localhost)(:\d+)?$/.test(req.headers.host || '')) return next(new HttpError(403, '仅支持本机访问'));
  if (!['GET', 'HEAD', 'OPTIONS'].includes(req.method) && req.headers.origin) {
    try { if (new URL(req.headers.origin).host !== req.headers.host) return next(new HttpError(403, '请求来源与工作台不一致')); }
    catch { return next(new HttpError(403, '请求来源无效')); }
  }
  next();
}
