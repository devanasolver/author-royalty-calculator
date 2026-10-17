# Uploading to KDP - the 10-minute walkthrough

You have `interior.pdf` and `cover.pdf` from this toolkit, and a checked
`metadata.json`. Here is the upload, with the traps marked.

## 1. Start the book

- kdp.amazon.com > Bookshelf > Create > Paperback (or Kindle eBook).
- Paste title, subtitle, author from `metadata.json` exactly. KDP is
  picky about matching the cover - the title on your cover file must
  match what you type here.

## 2. Content

- Upload `interior.pdf`. Wait for the processing spinner to finish
  completely before clicking anything else. If you upload a second file
  while the first is still processing, it can fail silently - reload
  the page between uploads.
- Print options: pick the trim size, ink, and paper you told the
  toolkit (`--trim`, `--ink-paper`). Mismatches here are the #1 reason
  covers get rejected.
- Bleed: "Bleed (PDF only)" only if you built with `--bleed`.
- Upload `cover.pdf`. If KDP complains about the size, run
  `kdp validate cover.pdf --cover --pages N` again - the page count you
  gave the cover must be the FINAL page count of the interior.
- Open the online Previewer. Flip through every page. This is where you
  catch margin and layout issues - the toolkit checks the file, the
  previewer shows you the book.

## 3. The traps

- **Spine text**: KDP prints it only on books over 79 pages. The
  toolkit already skips it below that.
- **Barcode**: KDP stamps its barcode bottom-right on your back cover.
  Keep that 2 x 1.2 inch area clear of anything important
  (`--guides` shows you the zone).
- **AI content**: if any text or images in the book are AI-generated,
  KDP requires you to say Yes to the AI-generated content question.
  Not disclosing can get your account in trouble.
- **ISBN**: the free KDP ISBN is fine for paperbacks sold on Amazon.
  You only need your own ISBN if you want your own imprint name.

## 4. Pricing

- `kdp royalty <price> --print --pages N` shows your exact printing
  cost, the 50%/60% tier boundary, and the lowest price KDP allows.
- Paperbacks priced under $9.99 (US) earn 50%, not 60% - sometimes
  pricing at $9.99 earns you MORE per sale than $8.99.
- eBooks: the 70% band is $2.99-$12.99. Outside it you get 35%.

## 5. After publishing

- Sales and royalties land in Reports. Download the "Prior Months'
  Royalties" Excel file and run `kdp report royalties.xlsx` for a
  summary by title and marketplace.
- Ready to advertise: `kdp ads --title "My Book" --price 9.99 --pages N`
  writes a starter plan and a keyword CSV for the Amazon Ads console.
