# Content → JSON mapping report

- Content file: `/mnt/user-data/uploads/_Manager_AS_Clayton_Electrical_1926506.docx`  
- Template: `/mnt/user-data/uploads/new-tem.json`  
- Mapping config: `mapping.albert-services-electrical.json`  
- Output: `out.json`

**Result:** PASSED · 58 fields written · 10 unchanged (identical wording) · 4 cloned element(s) · 10 warning(s) · 0 error(s)

## 1. Mapping summary

| Src § | Rule | Source content | → Template element | Field | Status |
|---|---|---|---|---|---|
| - | banner | (derived) Electrical | `3e4f198c` (heading) `content[0].elements[0]` | title | mapped |
| 2 | hero | Electrical Services in Clayton, OH | `1ad728c0` (heading) `content[1].elements[0].elements[0]` | title | mapped |
| 2 | hero | Albert Services provides complete electrical services for homeowners … / As a trusted electrical contractor, we offer both residential electri… / Need an emergency electrician fast? We provide 24 hour electrician se… | `3f7ba278` (text-editor) `content[1].elements[0].elements[1]` | editor | mapped |
| 3 | services-grid | Complete Electrical Services in Clayton | `2577d89d` (heading) `content[2].elements[0]` | title | mapped |
| 3 | services-grid | Whether you need a quick repair or a full installation, Albert Servic… | `ee18303` (text-editor) `content[2].elements[1]` | editor | mapped |
| 3 | services-grid | Electrical Services | `e5342d8` (call-to-action) `content[2].elements[2].elements[0]` | title | mapped |
| 3 | services-grid | Our complete electrical services cover repairs, maintenance, and inst… | `e5342d8` (call-to-action) `content[2].elements[2].elements[0]` | description | mapped |
| 3 | services-grid | Book Now | `e5342d8` (call-to-action) `content[2].elements[2].elements[0]` | button | unchanged (identical wording) |
| 3 | services-grid | Licensed Electrician Team | `2e867c8b` (call-to-action) `content[2].elements[2].elements[1]` | title | mapped |
| 3 | services-grid | Every job is completed by a licensed electrician you can trust. | `2e867c8b` (call-to-action) `content[2].elements[2].elements[1]` | description | mapped |
| 3 | services-grid | Book Now | `2e867c8b` (call-to-action) `content[2].elements[2].elements[1]` | button | unchanged (identical wording) |
| 3 | services-grid | Emergency Electrician | `5526e620` (call-to-action) `content[2].elements[2].elements[2]` | title | mapped |
| 3 | services-grid | Our emergency electrician team is ready to respond when you need help… | `5526e620` (call-to-action) `content[2].elements[2].elements[2]` | description | mapped |
| 3 | services-grid | Book Now | `5526e620` (call-to-action) `content[2].elements[2].elements[2]` | button | unchanged (identical wording) |
| 3 | services-grid | Trusted Electrical Contractor | `918548c` (call-to-action) `content[2].elements[2].elements[3]` | title | mapped |
| 3 | services-grid | As a trusted electrical contractor, we know Clayton homes inside and … | `918548c` (call-to-action) `content[2].elements[2].elements[3]` | description | mapped |
| 3 | services-grid | Book Now | `918548c` (call-to-action) `content[2].elements[2].elements[3]` | button | unchanged (identical wording) |
| 3 | services-grid | Residential Electrician Services | `7ca18942` (call-to-action) `content[2].elements[2].elements[4]` | title | mapped |
| 3 | services-grid | Our residential electrician services keep every part of your home's e… | `7ca18942` (call-to-action) `content[2].elements[2].elements[4]` | description | mapped |
| 3 | services-grid | Book Now | `7ca18942` (call-to-action) `content[2].elements[2].elements[4]` | button | unchanged (identical wording) |
| 3 | services-grid | 24 Hour Electrician | `78eb9414` (call-to-action) `content[2].elements[2].elements[5]` | title | mapped |
| 3 | services-grid | Electrical problems don't wait, and neither do we. Our 24 hour electr… | `78eb9414` (call-to-action) `content[2].elements[2].elements[5]` | description | mapped |
| 3 | services-grid | Book Now | `78eb9414` (call-to-action) `content[2].elements[2].elements[5]` | button | unchanged (identical wording) |
| 3 | services-grid | Electrical Repair Service | `4dff7448` (call-to-action) `(clone)` | title | mapped |
| 3 | services-grid | From outlets to panels, our electrical repair service resolves the is… | `4dff7448` (call-to-action) `(clone)` | description | mapped |
| 3 | services-grid | Book Now | `4dff7448` (call-to-action) `(clone)` | button | unchanged (identical wording) |
| 5 | specialists | Clayton's Trusted Electrical Specialists | `f8d8704` (heading) `content[3].elements[0].elements[0]` | title | mapped |
| 5 | specialists | When Clayton homeowners need dependable electrical services, Albert S… / As a trusted electrical contractor, every technician on our team is a… / Whether you need a residential electrician for routine work or an eme… | `1d672336` (text-editor) `content[3].elements[0].elements[1]` | editor | mapped |
| 6 | experienced | Experienced Electrical Services in Clayton, OH | `56db65e2` (heading) `content[4].elements[0]` | title | mapped |
| 6 | experienced | Fast, Reliable Repairs | `74d0cc6c` (image-box) `content[4].elements[1].elements[0]` | title_text | mapped |
| 6 | experienced | We diagnose issues efficiently and offer lasting repairs to restore y… | `74d0cc6c` (image-box) `content[4].elements[1].elements[0]` | description_text | mapped |
| 6 | experienced | Honest Recommendations | `748ac504` (image-box) `content[4].elements[1].elements[1]` | title_text | mapped |
| 6 | experienced | We explain your options clearly so you can make informed decisions wi… | `748ac504` (image-box) `content[4].elements[1].elements[1]` | description_text | mapped |
| 6 | experienced | Reliable Workmanship | `2cf86f1e` (image-box) `content[4].elements[1].elements[2]` | title_text | mapped |
| 6 | experienced | Every repair is completed using quality parts and proven techniques f… | `2cf86f1e` (image-box) `content[4].elements[1].elements[2]` | description_text | mapped |
| 6 | experienced | Schedule Service | `3fe535e3` (button) `content[4].elements[2]` | text | mapped |
| 7 | go-to-contractor | Clayton's Go-To Electrical Contractor Since 1998 | `17871ff0` (heading) `content[5].elements[0].elements[0]` | title | mapped |
| 7 | go-to-contractor | Albert Services has proudly served homeowners throughout Clayton and … / From routine maintenance to complex repairs, our electrical contracto… | `29c9b76b` (text-editor) `content[5].elements[0].elements[1]` | editor | mapped |
| 7 | go-to-contractor | Get In Touch | `7e524c4a` (button) `content[5].elements[0].elements[2]` | text | mapped |
| 8 | benefits | Benefits of Professional Electrical Services | `26377df3` (heading) `content[6].elements[0].elements[0]` | title | mapped |
| 8 | benefits | Professional electrical service offers more than a quick fix. It help… / Fast Diagnosis / Our technicians quickly identify the cause of electrical issues to mi… … | `88f074a` (text-editor) `content[6].elements[0].elements[1]` | editor | mapped |
| 9 | reliable-solutions | Reliable Electrical Solutions for Clayton Homes | `7094982a` (heading) `content[7].elements[0].elements[0]` | title | mapped |
| 9 | reliable-solutions | Electrical issues can affect any home, from minor repairs to major up… / Albert Services provides complete electrical services from our team o… | `55033ecf` (text-editor) `content[7].elements[0].elements[1]` | editor | mapped |
| 10 | why-choose | Why Homeowners Choose Albert Services | `6472341` (heading) `content[8].elements[0].elements[0]` | title | unchanged (identical wording) |
| 10 | why-choose | Designed Around Your Home | `50d6e8f4` (image-box) `content[8].elements[0].elements[1].elements[0]` | title_text | mapped |
| 10 | why-choose | Every service is planned with your home's specific electrical system … | `50d6e8f4` (image-box) `content[8].elements[0].elements[1].elements[0]` | description_text | mapped |
| 10 | why-choose | Skilled Technicians | `1605eef` (image-box) `content[8].elements[0].elements[1].elements[1]` | title_text | mapped |
| 10 | why-choose | Our technicians use proper testing and repair practices for safe, dep… | `1605eef` (image-box) `content[8].elements[0].elements[1].elements[1]` | description_text | mapped |
| 10 | why-choose | 30-Minute Arrival Window | `42fdedf9` (image-box) `content[8].elements[0].elements[1].elements[2]` | title_text | mapped |
| 10 | why-choose | We value your time by providing a convenient 30-minute arrival window… | `42fdedf9` (image-box) `content[8].elements[0].elements[1].elements[2]` | description_text | mapped |
| 10 | why-choose | Modern Product Options | `7389db81` (image-box) `content[8].elements[0].elements[1].elements[3]` | title_text | mapped |
| 10 | why-choose | Whether you need standard fixtures or upgraded electrical solutions, … | `7389db81` (image-box) `content[8].elements[0].elements[1].elements[3]` | description_text | mapped |
| 10 | why-choose | Clean Work Areas | `7494fae5` (image-box) `content[8].elements[0].elements[1].elements[4]` | title_text | mapped |
| 10 | why-choose | We protect your home during every job and leave the work area neat wh… | `7494fae5` (image-box) `content[8].elements[0].elements[1].elements[4]` | description_text | mapped |
| 10 | why-choose | Trusted Local Team | `30fc22d5` (image-box) `content[8].elements[0].elements[1].elements[5]` | title_text | mapped |
| 10 | why-choose | For decades, homeowners throughout Clayton and the Miami Valley have … | `30fc22d5` (image-box) `content[8].elements[0].elements[1].elements[5]` | description_text | mapped |
| 12 | faq | Clayton Electrical FAQs | `1dcb8196` (heading) `content[11].elements[1]` | title | mapped |
| 12 | faq | Q: Do you offer 24 hour electrician service for… / A: Yes. Our 24 hour electrician service means h… | `20c5a18b` (nested-accordion) `content[11].elements[2]` | items[0] + child editor 7b86e625 | mapped |
| 12 | faq | Q: What should I look for in an electrical cont… / A: A trustworthy electrical contractor should b… | `20c5a18b` (nested-accordion) `content[11].elements[2]` | items[1] + child editor 66cec799 | mapped |
| 12 | faq | Q: Is every technician a licensed electrician? / A: Yes. Every job is completed by a licensed el… | `20c5a18b` (nested-accordion) `content[11].elements[2]` | items[2] + child editor 7256f716 | mapped |
| 12 | faq | Q: Do you provide residential electrician servi… / A: Yes. Our residential electrician team servic… | `20c5a18b` (nested-accordion) `content[11].elements[2]` | items[3] + child editor 43f7f1e5 | mapped |
| 12 | faq | Q: How quickly can I get an emergency electrici… / A: Our emergency electrician team responds quic… | `20c5a18b` (nested-accordion) `content[11].elements[2]` | items[4] + child editor c0ec551e | mapped |
| 13 | final-cta | Need Reliable Home Service You Can Count On? | `10a269fc` (heading) `content[12].elements[0].elements[0]` | title | unchanged (identical wording) |
| 13 | final-cta | Whether you need electrical services, an emergency electrician, or he… | `4814ddb3` (text-editor) `content[12].elements[0].elements[1]` | editor | mapped |
| 13 | final-cta | Request A Free Estimate | `4bb1ab53` (button) `content[12].elements[0].elements[2].elements[0]` | text | unchanged (identical wording) |
| 13 | final-cta | Call Now | `6c1e6937` (button) `content[12].elements[0].elements[2].elements[1]` | text | mapped |
| 13 | final-cta | Get In Touch | `adc65c70` (button) `(clone)` | text | mapped |
| - | page | (derived) document title | `(page)` (page) `title` | title | mapped |

## 2. Unmatched source content (no template element)

**Source section 4 (table 4)** - no rule maps it; template has no clear counterpart:
- label: Real Jobs We've Completed Near You
- placeholder: *Insert Case Studies Here*

**Source section 11 (table 11)** - no rule maps it; template has no clear counterpart:
- label: Your Trusted Home Service Experts Across the Miami Valley
- listitem: Dayton
- listitem: Miamisburg
- listitem: Bellbrook
- listitem: Riverside
- listitem: Centerville
- listitem: Springboro
- listitem: Oakwood
- listitem: Huber Heights
- listitem: Kettering
- listitem: Beavercreek
- listitem: West Carrollton
- listitem: Englewood
- button: See All Service Areas
- button: See All Service Areas
- button: See All Service Areas
- button: See All Service Areas


### Intentionally ignored (by config)

- Section 0 (table 0): Site header (logo text, Schedule Online / Call buttons) - lives in the theme header template, not in this page JSON  — text: Albert Services; *Schedule Online Button*; *Call Button*
- Section 1 (table 1): Main navigation - theme menu, not in this page JSON  — text: Home; About; Heating; Cooling; Plumbing; Drains; Electrical; Slab Leak; Specials; Financing
- Section 14 (table 14): Site footer (logo, quick links, services, useful links, contact details) - theme footer template, not in this page JSON  — text: *Insert Client Logo*; Quick Links; Services; Useful Links; Contact Information; *Insert Tagline*; [Social Media Buttons]; Home; About; Specials; Financing; Heating

### Source placeholders (instructions, no content to map)

- Section 0: '*Schedule Online Button*'
- Section 0: '*Call Button*'
- Section 2: 'Insert Contact Form Here'
- Section 3 (card 'Electrical Services'): 'Insert Image Here'
- Section 3 (card 'Licensed Electrician Team'): 'Insert Image Here'
- Section 3 (card 'Emergency Electrician'): 'Insert Image Here'
- Section 3 (card 'Trusted Electrical Contractor'): 'Insert Image Here'
- Section 3 (card 'Residential Electrician Services'): 'Insert Image Here'
- Section 3 (card '24 Hour Electrician'): 'Insert Image Here'
- Section 3 (card 'Electrical Repair Service'): 'Insert Image Here'
- Section 4: '*Insert Case Studies Here*'
- Section 5: 'Insert Image'
- Section 7: 'Insert Image'
- Section 8: 'Insert Image'
- Section 9: 'Insert Image'
- Section 13: 'Insert Image'
- Section 14: '*Insert Client Logo*'
- Section 14: '*Insert Tagline*'
- Section 14: '[Social Media Buttons]'
- Section 14: '*Insert Contact Details*'

### Document notes (header/footer text, not page content)

- Disclaimer: Please note that this content has been proofread manually and through grammar checkers to eliminate spacing errors. Any spacing errors you may come across are due to compatibility issues in Microsoft Word.

## 3. Template fields retained (no source value)

| Element | Widget.field | Current value | Reason |
|---|---|---|---|
| `a68a826` | button.text | Call 937-444-4357 | Hero call button: source has no hero button and no phone number ('Call Button' / '*Insert Contact Details*' are placeholders). Template label and tel: link kept - confirm the number. |
| `19602cd3` | template.template_id | global template #422 | Satisfies source placeholder '*Insert Contact Form Here*' (form lives in global template #422) |
| `55e5ac2a` | button.text | Schedule Service | No button text in source section 5 (Clayton's Trusted Electrical Specialists); template button kept |
| `155ae91c` | heading.title | What Our Client Says | Testimonials block - not present in the content file |
| `2743f7a9` | shortcode.shortcode | [trustindex no-registration=google] | Testimonials shortcode - not present in the content file |
| `1a652e61` | template.template_id | global template #449 | Global template #449 - content lives outside this JSON. Possibly where the source 'Service Areas' / 'Real Jobs' blocks belong; unknown - confirm. |
| `46239fd6` | heading.title | FAQ | Eyebrow label above the FAQ heading; source has no equivalent |

### Media retained from template (source only has placeholders)

- `e5342d8` call-to-action `content[2].elements[2].elements[0]` url=(empty) alt=''
- `2e867c8b` call-to-action `content[2].elements[2].elements[1]` url=(empty) alt=''
- `5526e620` call-to-action `content[2].elements[2].elements[2]` url=(empty) alt=''
- `918548c` call-to-action `content[2].elements[2].elements[3]` url=(empty) alt=''
- `7ca18942` call-to-action `content[2].elements[2].elements[4]` url=(empty) alt=''
- `78eb9414` call-to-action `content[2].elements[2].elements[5]` url=(empty) alt=''
- `75f9d86f` image `content[3].elements[1].elements[0]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/09/expert-heating-services-in-bellbrook-oh.jpg alt='' ⚠ stale: bellbrook,heating
- `74d0cc6c` image-box `content[4].elements[1].elements[0]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/08/ab-icons-2.png alt=''
- `748ac504` image-box `content[4].elements[1].elements[1]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/08/ab-icons-1.png alt=''
- `2cf86f1e` image-box `content[4].elements[1].elements[2]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/08/sec-icons-3.png alt=''
- `1f15c5e7` image `content[5].elements[1].elements[0]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/08/ab-2.webp alt=''
- `6cfe06eb` image `content[6].elements[1].elements[0]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/09/professional-heating-services-in-bellbrook-oh.jpg alt='' ⚠ stale: bellbrook,heating
- `26c5c78` image `content[7].elements[1].elements[0]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/09/trusted-heating-services-in-bellbrook-oh.jpg alt='' ⚠ stale: bellbrook,heating
- `50d6e8f4` image-box `content[8].elements[0].elements[1].elements[0]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/08/ab-icons-1.png alt=''
- `1605eef` image-box `content[8].elements[0].elements[1].elements[1]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/08/sec-icons-3.png alt=''
- `42fdedf9` image-box `content[8].elements[0].elements[1].elements[2]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/08/Group-1261158417.png alt=''
- `7389db81` image-box `content[8].elements[0].elements[1].elements[3]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/08/Group-1261158420.png alt=''
- `7494fae5` image-box `content[8].elements[0].elements[1].elements[4]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/08/sec-icons-5.png alt=''
- `30fc22d5` image-box `content[8].elements[0].elements[1].elements[5]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/08/loc-img.png alt=''
- `4f004f1d` image `content[12].elements[1].elements[0]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/09/cta-img1.webp alt=''
- `4dff7448` call-to-action `(clone)` url=(empty) alt=''

## 4. Warnings / ambiguities

- DERIVED: var 'city' = 'Clayton' derived from document title 'Albert Services -- Clayton Electrical Web Page' (not an explicit content element) - please confirm
- DERIVED: var 'service' = 'Electrical' derived from document title 'Albert Services -- Clayton Electrical Web Page' (not an explicit content element) - please confirm
- [hero] heading 1ad728c0: template had an accent <span> ('Stay Warm with Reliable Heating Services in Bellbrook'); source gives plain text so the accent was dropped (set 'span_last_words' on the bind to re-apply)
- [services-grid] source has 7 items but template container 4cacd431 has 6; cloned slot 78eb9414 x1 (new keys follow the cloned widget; review link/style)
- [faq] heading 1dcb8196: template had an accent <span> ('Frequently Asked Questions'); source gives plain text so the accent was dropped (set 'span_last_words' on the bind to re-apply)
- [faq] accordion had 4 items, source has 5; cloned last item/container x1
- [final-cta] source has 3 items but template container 6fbae189 has 2; cloned slot 4bb1ab53 x1 (new keys follow the cloned widget; review link/style)
- STALE TEMPLATE MEDIA retained in 75f9d86f (image): file name contains ['bellbrook', 'heating'] - replace image
- STALE TEMPLATE MEDIA retained in 6cfe06eb (image): file name contains ['bellbrook', 'heating'] - replace image
- STALE TEMPLATE MEDIA retained in 26c5c78 (image): file name contains ['bellbrook', 'heating'] - replace image

## 5. Validation

- ✅ JSON serialises and re-parses
- ✅ Template structure, key names and data types preserved
- ✅ New elements exist only as logged clones - 4 clone(s) logged
- ✅ Element ids unique - 93 elements
- ✅ Accordion items match child containers
- ✅ No relevant source node silently skipped - 2 unmapped section(s), 0 unmapped node(s) in mapped sections - all reported
- ✅ No source node mapped to two different targets
- ✅ Every mapped text appears verbatim in its target field
- ✅ Source wording unmodified (spot check on whole output)
- ✅ No stale template terms left in text fields - terms checked: ['bellbrook', 'furnace', 'heat pump', 'heating', 'thermostat']

### Cloned elements

- `4dff7448` cloned from `78eb9414` (rule services-grid)
- `694a2bd5` cloned from `1edb0c3c` (rule faq)
- `c0ec551e` cloned from `43f7f1e5` (rule faq)
- `adc65c70` cloned from `4bb1ab53` (rule final-cta)
