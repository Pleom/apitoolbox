!(function (e, t) {
  "object" == typeof exports && "undefined" != typeof module
    ? t(exports)
    : "function" == typeof define && define.amd
    ? define(["exports"], t)
    : t(
        ((e =
          "undefined" != typeof globalThis
            ? globalThis
            : e || self).ApiToolBox = {})
      );
})(this, function (e) {
  "use strict";
  class t extends Error {
    constructor(e) {
      super(e), (this.name = "ToolCallError");
    }
  }
  (e.ToolCallError = t),
    (e.UserClient = class e {
      constructor(e = []) {
        for (let t of ((this.config = {}), e)) this.config[t.name] = t.config;
      }
      async callTool(e, o = {}) {
        if (!e) throw new t("Tool object is required");
        let r = this.config[e.serviceName];
        if (!r)
          throw new t(`No configuration found for service '${e.serviceName}'`);
        let n = {};
        if (e.headers && Array.isArray(e.headers)) {
          for (let i of e.headers)
            if (i.name && i.required) {
              if (r[i.name]) n[i.name] = r[i.name];
              else
                throw new t(
                  `Required header '${i.name}' not found in service configuration`
                );
            }
        }
        let s = e.endpoint,
          a = /\{([^}]+)\}/g,
          f = [],
          c;
        for (; null !== (c = a.exec(e.endpoint)); ) f.push(c[1]);
        for (let l of f)
          if (o.parameters && o.parameters[l])
            s = s.replace(`{${l}}`, o.parameters[l]);
          else throw new t(`Missing required path parameter: ${l}`);
        let d = new URL(s);
        if (o.parameters)
          for (let [h, u] of Object.entries(o.parameters))
            f.includes(h) || d.searchParams.set(h, String(u));
        let p = { method: e.method || "GET", headers: n };
        o.body &&
          Object.keys(o.body).length > 0 &&
          ("string" == typeof o.body
            ? (p.body = o.body)
            : ((p.body = JSON.stringify(o.body)),
              (n["Content-Type"] = "application/json")));
        try {
          let m = await fetch(d.toString(), p);
          if (!m.ok)
            throw new t(
              `API request failed with status ${m.status}: ${m.statusText}`
            );
          let g = await m.json();
          return g;
        } catch (w) {
          if (w instanceof t) throw w;
          throw new t(
            `Network error: ${w instanceof Error ? w.message : "Unknown error"}`
          );
        }
      }
      getConfig() {
        return { ...this.config };
      }
      updateConfig(e) {
        this.config = { ...this.config, ...e };
      }
    });
});
