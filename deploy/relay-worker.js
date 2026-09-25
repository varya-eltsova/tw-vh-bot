// Посредник между Telegram и виртуальным хостингом (Cloudflare Worker).
// С хостинга api.telegram.org недоступен, а Telegram не может достучаться
// до хостинга, поэтому запросы в обе стороны идут через этот Worker.
//
// Переменные Worker (Settings -> Variables and Secrets):
//   BOT_ID          - число до двоеточия в токене бота
//   BOT_WEBHOOK_URL - https://<домен сайта>/webhook

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Исходящие: бот на хостинге -> Telegram API
    if (url.pathname.startsWith("/bot")) {
      if (!url.pathname.startsWith(`/bot${env.BOT_ID}:`)) {
        return new Response("Forbidden", { status: 403 });
      }
      return fetch("https://api.telegram.org" + url.pathname + url.search, {
        method: request.method,
        headers: { "Content-Type": request.headers.get("Content-Type") || "" },
        body: request.method === "GET" ? undefined : request.body,
      });
    }

    // Входящие: Telegram -> бот на хостинге
    if (url.pathname === "/webhook" && request.method === "POST") {
      return fetch(env.BOT_WEBHOOK_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-Telegram-Bot-Api-Secret-Token":
            request.headers.get("X-Telegram-Bot-Api-Secret-Token") || "",
        },
        body: request.body,
      });
    }

    return new Response("Not found", { status: 404 });
  },
};
