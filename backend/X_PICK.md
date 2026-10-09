# Daily X pick (for the Wiener Dog of the Day routine)

The GitHub Action (`.github/workflows/daily-dog.yml`, ~9:17 AM ET) always picks a
random Reddit "hidden gem" first. The daily routine runs **after** it (9:30 AM ET
or later) and either:

- **X day:** replaces today's entry with a quirky/heartwarming dachshund (wiener dog / sausage dog / doxie) post from X, or
- **Reddit day:** keeps the Reddit pick and just adds a short blurb.

Aim for a mix (roughly every other day on X, never more than 2 X days in a row
and never 3 Reddit days in a row). Check the archive to see what recent days used:
`python3 -c "import json;[print(d['date'],d.get('source'),d.get('subreddit')) for d in json.load(open('backend/data/archive.json'))['days'][:7]]"`

Repo: `/workspace/wiener-dog-of-the-day` (GitHub `jm88825/wiener-dog-of-the-day`). Always start with
`git pull --rebase origin main` because the bot commits data every morning.

## 1. Search X (one call, keep it cheap)

MCP server `user-X`, tool **`search_posts_all`** (there is no `search_posts_recent`
on this connector). Arguments (adapted from the Cat of the Day query that worked
on 2026-10-02, with the lessons below already applied):

```json
{
  "query": "(dachshund OR doxie OR \"wiener dog\" OR \"weiner dog\" OR \"sausage dog\" OR \"my dachshund\") (has:images OR has:videos) -has:hashtags -is:retweet -is:reply -is:quote -is:nullcast lang:en -giveaway -sale -shop -nft -crypto -adopt -breeder -puppies4sale -stud -\"for sale\" -\"hot dog\" -recipe",
  "max_results": 12,
  "sort_order": "relevancy",
  "start_time": "<now minus ~48h, ISO 8601 UTC, e.g. 2026-09-30T23:00:00Z>",
  "expansions": "attachments.media_keys,author_id",
  "media.fields": "type,url,preview_image_url,variants,width,height,duration_ms,alt_text",
  "post.fields": "created_at,public_metrics,possibly_sensitive,lang,attachments",
  "user.fields": "username,name,verified"
}
```

Facts learned from the Cat of the Day test runs (same connector, same tier):

- **`min_faves:` is NOT available** on this API tier ("Operator is not available in
  current product"); the request fails (no charge). Filter on
  `public_metrics.like_count` yourself.
- Cost: 12 posts = **$0.06** (≈ $0.005/post; the user expansion added nothing
  measurable). Check with `get_usage_credits` (free) before/after. Keep
  `max_results` ≤ 20 (≤ $0.10/day).
- With that query, relevancy results were mostly hashtag spam and promo accounts
  with 0–2 likes, hence **`-has:hashtags`** (every spam post had hashtags; the
  good one had none). For dachshunds also watch out for breeders/puppy sellers,
  "sausage dog" food posts and hot-dog jokes; `-breeder -"for sale" -"hot dog"`
  removes most. If a search turns up nothing usable, make it a Reddit day
  instead of paying for more searches.
- Each post has a `url` field (`https://x.com/<handle>/status/<id>`) and its media
  are in `includes.media` (match `attachments.media_keys[0]` to `media_key`);
  the author is in `includes.users` (match `author_id` to `id`).

## 2. Choose a post

Must:
- Clearly a real dachshund (or dachshund mix) in the media: long body, short
  legs, floppy ears. Download and **look at it** (photo `url` + `?name=small`, or
  the video's `preview_image_url`). Not a hot dog, a plush toy, a costume on
  another breed, or a drawing.
- `possibly_sensitive: false`, safe for work, no injury/gore/death, not sad.
- Not an ad, shop, breeder/puppy sale, giveaway, link farm, crypto/NFT, AI-art
  account, or a post that is mostly hashtags/links. Not a reply/quote/retweet.
  No lost-dog / rescue-appeal / vet-emergency posts (sad, and the dog may not
  be safe).
- Quirky, funny, or heartwarming, from a normal person.
- Not already in `backend/data/archive.json` (the importer refuses repeats).

Prefer: a "hidden gem" (not mega-viral; skip >50K likes), real engagement if
available (≥ 20 likes is nice but a lovely 7-like post is fine), video with sound
or a sharp photo, posted in the last 1–2 days.

## 3. Write the pick JSON

Save as `backend/picks/<date>-x.json` (committed as a record):

```json
{
  "source": "x",
  "date": "2026-10-10",
  "postUrl": "https://x.com/<handle>/status/<id>",
  "authorHandle": "<handle>",
  "authorName": "<display name>",
  "likes": 42,
  "title": "<short headline in the poster's own words>",
  "text": "<the post's full text, copied verbatim>",
  "blurb": "<1–2 sentences, see below>",
  "xMedia": { "<the post's media object copied verbatim from includes.media>": "" }
}
```

- `title`: a short headline taken from the post's own words (≤ ~90 chars). If
  omitted, the first sentence of `text` is used.
- `xMedia`: paste the media object as-is (`type`, `url` / `preview_image_url`,
  `variants`, `width`, `height`). The importer picks the media for you:
  - `photo` → `mediaType: "image"`, `mediaUrl` = `url`, thumbnail = `url?name=small`
  - `video` → highest-bitrate `video/mp4` variant ≤ 2.5 Mbps as `mediaUrl`
    (X MP4s include audio), the `.m3u8` variant as `hlsUrl`,
    `preview_image_url` as poster; it confirms audio with ffprobe/the playlist
    and measures loudness if ffmpeg is installed.
  - `animated_gif` → silent looping video.
  Multi-photo posts: only the first media item is shown; pick the best one by
  copying that media object.
- Instead of `xMedia` you can give `mediaType`, `mediaUrl`, `thumbnail`/`posterUrl`,
  `hlsUrl`, `width`, `height` directly (media must be on pbs.twimg.com / video.twimg.com).

### The blurb (also used on Reddit days)

1–2 sentences, ≤ 300 characters, warm and a little playful. Base it **only** on
the post's own text and what is actually visible in the photo/video. Don't invent
names, ages, breeds, backstories or feelings the post doesn't support. Refer to
the poster neutrally ("their human", "the poster"). No hashtags or emojis needed.

Style example (illustrative, not a real post): "This little red doxie has
claimed the sunniest spot on the couch and is stretched out to full sausage
length. Their human says she refuses to move until dinner."

## 4. Import and check

```bash
cd /workspace/wiener-dog-of-the-day
git pull --rebase origin main
python3 backend/pick_dog.py --from-json backend/picks/2026-10-10-x.json --dry-run   # check output
python3 backend/pick_dog.py --from-json backend/picks/2026-10-10-x.json
```

This replaces today's entry in `backend/data/latest.json` and `archive.json`
(the date defaults to today in New York time; set `"date"` to be explicit).
Once today's entry is an X pick, the scheduled Reddit run won't overwrite it
(unless someone passes `--force`).

**Reddit day instead:** look at today's Reddit media (`thumbnail` or `mediaUrl`
in `latest.json`), then:

```bash
python3 backend/pick_dog.py --set-blurb "A tiny black-and-tan doxie ... full sausage length."
```

(`--set-blurb ""` removes a blurb; `--date YYYY-MM-DD` targets another day.)

## 5. Publish

```bash
cd /workspace/wiener-dog-of-the-day
git add backend/data backend/picks
git commit -m "Wiener dog of the day: <date> (X: @handle)"     # or "... blurb"
git pull --rebase origin main
git -c credential.helper= -c credential.helper='!gh auth git-credential' push origin main
```

GitHub Pages updates within a few minutes; the app picks it up on its next
load / pull-to-refresh. Check https://jm88825.github.io/wiener-dog-of-the-day/backend/data/latest.json.

## Data shape (what the importer writes)

X entries also keep the legacy fields (inherited from Cat of the Day): `author` = handle, `permalink` = post URL, `score` = likes,
`scoreLabel` = "likes", `subreddit` = null. New fields: `source: "x"`,
`authorHandle`, `authorName`, `postUrl`, `postId`, `likes`, `text`, `blurb`,
`mediaType`, `mediaUrl`, `thumbnail` (poster), `width`, `height`, and for video
`hlsUrl`, `bitRate`, `hasAudio`, `mp4HasAudio`, `hlsHasAudio`, `audioMeanDb`,
`audioMaxDb`, `audioQuiet`.

Note: video.twimg.com returns 403 to browsers that send a non-X `Referer`. The
Android app sends none; the web build adds `<meta name="referrer" content="no-referrer">`.
