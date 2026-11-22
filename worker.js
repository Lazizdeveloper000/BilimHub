// =========================================================
// BilimHub — Cloudflare Worker (Telegram Bot va Savollar API)
// Bot: @BilimHubb1bot
// =========================================================

const _d = (s) => (typeof atob === "function" ? atob(s) : Buffer.from(s, "base64").toString("utf-8"));
const BOT_TOKEN = _d("OTAyMDcyODg3NTpBQUU2SG03OHRMSGNVNWZVbmZIR216U1Y0UmJvNkJ6Uy1XUQ==");
const ADMIN_ID = _d("ODk5MDU4NTc3MA==");

export default {
  async fetch(request, env) {
    const token = env?.BOT_TOKEN || BOT_TOKEN;
    const adminId = env?.ADMIN_ID || ADMIN_ID;

    const cors = {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type"
    };

    if (request.method === "OPTIONS") {
      return new Response(null, { headers: cors });
    }

    const url = new URL(request.url);

    // 1. Saytdagi Savollar / Fikrlar formasi yuborganda
    if (url.pathname === "/feedback" || url.pathname === "/api/feedback") {
      if (request.method !== "POST") {
        return new Response("Faqat POST so'rovi qabul qilinadi", { status: 405, headers: cors });
      }
      try {
        const body = await request.json();
        const name = String(body.name || "Noma'lum").trim().slice(0, 60);
        const text = String(body.text || "").trim().slice(0, 500);

        if (!text) {
          return new Response(JSON.stringify({ ok: false, error: "Xabar matni bo'sh" }), {
            status: 400,
            headers: { ...cors, "Content-Type": "application/json" }
          });
        }

        const esc = s => s.replace(/[&<>]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
        const tgMsg = `💬 <b>BilimHub — yangi savol / taklif</b>\n\n` +
                      `👤 <b>Kimdan:</b> ${esc(name)}\n` +
                      `📝 <b>Xabar:</b>\n${esc(text)}\n\n` +
                      `⏰ <b>Vaqt:</b> ${new Date().toLocaleString("uz-UZ", { timeZone: "Asia/Tashkent" })}`;

        const tgRes = await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ chat_id: adminId, text: tgMsg, parse_mode: "HTML" })
        });

        const data = await tgRes.json();
        return new Response(JSON.stringify({ ok: data.ok }), {
          headers: { ...cors, "Content-Type": "application/json" }
        });
      } catch (err) {
        return new Response(JSON.stringify({ ok: false, error: err.message }), {
          status: 500,
          headers: { ...cors, "Content-Type": "application/json" }
        });
      }
    }

    // 2. Telegram Webhook (Foydalanuvchilar botga yozganda avtomatik javob)
    if (request.method === "POST") {
      try {
        const update = await request.json();
        const msg = update.message;
        if (msg && msg.text) {
          let reply = "Assalomu alaykum! BilimHub botiga xush kelibsiz. Saytimiz: bilimhub.uz";
          if (msg.text === "/start") {
            reply = "Assalomu alaykum! Men BilimHub rasmiy botiman. Sayt orqali yuborilgan barcha savollar va takliflar shu yerga keladi.";
          }
          await fetch(`https://api.telegram.org/bot${token}/sendMessage`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ chat_id: msg.chat.id, text: reply })
          });
        }
      } catch (e) {}
      return new Response("ok", { headers: cors });
    }

    return new Response("BilimHub Telegram Bot Worker muvaffaqiyatli ishlamoqda!", { headers: cors });
  }
};
