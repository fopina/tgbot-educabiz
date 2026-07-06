# tgbot-educabiz

Telegram bot for Educabiz.

## Configuration

The bot reads configuration from environment variables and from `.env.app` when
that file exists. Any setting can also be loaded from a file by using the same
name with a `_FILE` suffix. For example, `TGEB_TOKEN_FILE=/run/secrets/bot_token`
loads `TGEB_TOKEN` from that file.

Required settings:

```env
TGEB_TOKEN=123456:telegram-bot-token

TGEB_LOGIN_SCHOOL1_USERNAME=parent@example.com
TGEB_LOGIN_SCHOOL1_PASSWORD=school-1-password

TGEB_CHATID_123456789=SCHOOL1
```

`TGEB_CHATID_<telegram chat id>` maps a Telegram chat to one or more Educabiz
login profiles. To include multiple profiles in the same chat, separate profile
names with commas.

Supported settings:

| Variable | Required | Default | Description |
| --- | --- | --- | --- |
| `TGEB_TOKEN` | Yes | | Telegram bot token. |
| `TGEB_LOGIN_<profile>_USERNAME` | Yes | | Educabiz username for a named login profile. |
| `TGEB_LOGIN_<profile>_PASSWORD` | Yes | | Educabiz password for the same login profile. |
| `TGEB_CHATID_<telegram chat id>` | Yes | | Comma-separated list of login profiles allowed in that Telegram chat. |
| `TGEB_DEBUG` | No | `false` | Set to `true` to enable debug logging. |
| `TGEB_ABSENT_DEFAULT_NOTE` | No | | Note sent when marking a child absent/sick. |
| `TGEB_WEBHOOK_URL` | No | | Public webhook URL. When set, the bot uses Telegram webhooks instead of polling. |
| `TGEB_WEBHOOK_PORT` | No | `9999` | Local port used by the webhook server. |
| `TGEB_WEBHOOK_LISTEN` | No | | Local address used by the webhook server. |

The `_FILE` suffix works for all of these variables, including grouped
variables such as `TGEB_LOGIN_SCHOOL1_PASSWORD_FILE` or
`TGEB_CHATID_123456789_FILE`.

Without `TGEB_WEBHOOK_URL`, the bot runs with Telegram long polling. With
`TGEB_WEBHOOK_URL`, it starts a webhook server on `TGEB_WEBHOOK_PORT`. Set
`TGEB_WEBHOOK_LISTEN` to choose the local address the webhook server binds to.

## Using Multiple Schools

This note is copied from the
[`python-educabiz` README](https://github.com/fopina/python-educabiz#using-multiple-schools).

Educabiz does not provide a way to choose the school during login, matching the
behavior of the Educabiz mobile app.

The portal redirects to the right school based on the unique email/password
combination, so when using multiple schools with the same email address, use the
password associated with the intended school. If the same password is currently
used for multiple schools, log in to the first school that opens and change the
password there.

The old password will then redirect to the other school.

Example with two schools using the same email address and different passwords:

```env
TGEB_TOKEN=123456:telegram-bot-token

TGEB_LOGIN_SCHOOL1_USERNAME=parent@example.com
TGEB_LOGIN_SCHOOL1_PASSWORD=password-for-first-school

TGEB_LOGIN_SCHOOL2_USERNAME=parent@example.com
TGEB_LOGIN_SCHOOL2_PASSWORD=password-for-second-school

TGEB_CHATID_123456789=SCHOOL1,SCHOOL2
```

In this example, messages in Telegram chat `123456789` can use both Educabiz
profiles. `SCHOOL1` and `SCHOOL2` are just profile names; the bot matches them
to the corresponding `TGEB_LOGIN_<profile>_USERNAME` and
`TGEB_LOGIN_<profile>_PASSWORD` variables.

## Development

Check [CONTRIBUTING.md](CONTRIBUTING.md)
