# Security Policy

## Reporting a vulnerability

If you discover a security issue, please **do not open a public issue**. Email the maintainer at [simeonkolchin@gmail.com](mailto:simeonkolchin@gmail.com) with details and reproduction steps. You can expect an acknowledgement within a few days.

## Secrets

- All credentials (`TELEGRAM_BOT_TOKEN`, `YANDEX_DISK_TOKEN`) are read from the environment via `os.environ`.
- They must live only in your local `.env`, which is gitignored. `.env.example` ships placeholders only.

## ⚠️ Known exposure in git history

Earlier commits of this repository contained hard-coded credentials:

- a **Telegram bot token** in `app/bot/telegram_bot.py`
- a **Yandex Disk OAuth token** in `app/bot/yandex_disk.py`

The current tree no longer contains these — both are read from the environment. **However, the old values remain reachable in git history.** They must be treated as compromised and **rotated**:

- Revoke and reissue the Telegram token via [@BotFather](https://t.me/BotFather) (`/revoke`).
- Revoke the Yandex Disk OAuth token in the [Yandex OAuth console](https://oauth.yandex.com/) and issue a new one.

Rotating the credentials is the only reliable fix, since rewriting history does not guarantee the old values were never captured.
