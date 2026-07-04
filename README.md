# tgbot-educabiz

Telegram bot for Educabiz.

## Configuration

The bot reads configuration from environment variables and from `.env.app` when
that file exists.

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

## Using Multiple Schools

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

```sh
uv sync --dev
make test
make lint
```
