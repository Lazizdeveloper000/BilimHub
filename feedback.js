// Vercel serverless funksiya: /api/feedback
// Token va chat ID bu yerda YOZILMAYDI — Vercel > Settings > Environment Variables ichida turadi.
module.exports = async (req, res) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "POST") return res.status(405).json({ ok: false });

  const { name = "", text = "", hp = "" } = req.body || {};
  if (hp) return res.status(200).json({ ok: true }); // spam tuzoq maydon
  const n = String(name).trim().slice(0, 60);
  const m = String(text).trim().slice(0, 500);
  if (!n || !m) return res.status(400).json({ ok: false });

  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chat = process.env.TELEGRAM_CHAT_ID;
  if (!token || !chat) return res.status(500).json({ ok: false });

  const esc = (s) => s.replace(/[&<>]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;" }[c]));
  const body = "💬 <b>BilimHub — yangi savol / fikr</b>\n👤 " + esc(n) + "\n\n" + esc(m);

  try {
    const r = await fetch("https://api.telegram.org/bot" + token + "/sendMessage", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ chat_id: chat, text: body, parse_mode: "HTML" }),
    });
    return res.status(r.ok ? 200 : 502).json({ ok: r.ok });
  } catch (e) {
    return res.status(502).json({ ok: false });
  }
};
