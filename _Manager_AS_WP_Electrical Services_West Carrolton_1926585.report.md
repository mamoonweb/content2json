# Content → JSON mapping report

- Content file: `_Manager_AS_WP_Electrical Services_West Carrolton_1926585.docx`  
- Template: `new-tem.json`  
- Mapping config: `(web UI)`  
- Output: `_Manager_AS_WP_Electrical Services_West Carrolton_1926585.json`

**Result:** PASSED · 11 fields written · 1 unchanged (identical wording) · 0 cloned element(s) · 0 warning(s) · 0 error(s)

## 1. Mapping summary

| Content section | Rule | Source content | → Template element | Field | Status |
|---|---|---|---|---|---|
| 3 | template-section-1 | Complete Electrical Services for Homes in West Carrollton / Electrical Repairs / Electrical Panel Upgrades … | `3f7ba278` (text-editor) `content[1].elements[0].elements[1]` | editor | mapped |
| 3 | template-section-1 | Book Now | `a68a826` (button) `content[1].elements[0].elements[2]` | text | mapped |
| 8 | template-section-2 | When You Need a 24 Hour Electrician | `2577d89d` (heading) `content[2].elements[0]` | title | mapped |
| 8 | template-section-2 | Electrical emergencies don't always happen during normal business hou… / Our team responds quickly to urgent situations, helping homeowners pr… | `ee18303` (text-editor) `content[2].elements[1]` | editor | mapped |
| 10 | template-section-3 | Why Homeowners Choose Albert Services | `f8d8704` (heading) `content[3].elements[0].elements[0]` | title | mapped |
| 10 | template-section-3 | Since 1998, we've proudly served homeowners throughout Dayton with de… / We respect your time. Instead of asking you to wait around all day, w… / We explain every option clearly so you can make informed decisions wi… … | `1d672336` (text-editor) `content[3].elements[0].elements[1]` | editor | mapped |
| 10 | template-section-3 | Local Experience | `55e5ac2a` (button) `content[3].elements[0].elements[2]` | text | mapped |
| 11 | template-section-5 | Your Trusted Home Service Experts Across the Miami Valley /  Dayton /  Miamisburg … | `29c9b76b` (text-editor) `content[5].elements[0].elements[1]` | editor | mapped |
| 11 | template-section-5 | See All Service Areas | `7e524c4a` (button) `content[5].elements[0].elements[2]` | text | mapped |
| 13 | template-section-12 | Need Reliable Home Service You Can Count On? / Whether you're dealing with a plumbing issue, an aging air conditione… | `4814ddb3` (text-editor) `content[12].elements[0].elements[1]` | editor | mapped |
| 13 | template-section-12 | Request A Free Estimate | `4bb1ab53` (button) `content[12].elements[0].elements[2].elements[0]` | text | unchanged (identical wording) |
| 13 | template-section-12 | Call Button | `6c1e6937` (button) `content[12].elements[0].elements[2].elements[1]` | text | mapped |

## 2. Unmatched source content (no template element)

**Source section 2 (table 2)** - no rule maps it; template has no clear counterpart:
- label: Electrical Services in West Carrollton
- placeholder: *Insert Contact Form Here*
- paragraph: Keeping your home's electrical system safe and reliable is essential for your family's comfort and peace of mind. At Albert Services, we provide dependable electrical services for homeowners throughout West Carrollton. Whether you're dealing with flickering lights, outdated wiring, or an unexpected power issue, our experienced team is ready to help with prompt, professional solutions tailored to your home's needs.
- paragraph: Whether you need a quick repair or a complete electrical upgrade, our team is ready to help. Contact Albert Services today to schedule an appointment with a trusted licensed electrician serving West Carrollton.

- Section 10: `button` not placed anywhere: '30-Minute Arrival Window'
- Section 10: `button` not placed anywhere: 'Honest Recommendations'
- Section 10: `button` not placed anywhere: 'Skilled Technicians'
- Section 10: `button` not placed anywhere: 'Modern Solutions'
- Section 10: `button` not placed anywhere: 'Customer-First Service'

### Intentionally ignored (by config)

- Section 0 (table 0): marked as not page content in the UI  — text: Albert Services; *Schedule Online Button*; *Call Button*
- Section 1 (table 1): marked as not page content in the UI  — text: Home; About; Heating; Cooling; Plumbing; Drains; Electrical; Slab Leak; Specials; Financing
- Section 3 (table 3): marked as not page content in the UI  — text: Complete Electrical Services …; *Insert Image Here*; *Insert Image Here*; Electrical Repairs; Electrical Panel Upgrades; Restore power and resolve com…; Modernize aging electrical pa…; Book Now; Book Now; *Insert Image Here*; *Insert Image Here*; Lighting Installation
- Section 4 (table 4): marked as not page content in the UI  — text: Real Jobs We've Completed Nea…; *Insert Case Studies Here*
- Section 5 (table 5): marked as not page content in the UI  — text: Reliable Electrical Repair Se…; Electrical issues often begin…; Frequently tripped breakers; Flickering or dimming lights; Warm switches or outlets; Buzzing sounds from electrica…; Burning odors near outlets; Dead outlets; Sudden power loss in part of …; Our technicians carefully ins…; *Insert Image Here*
- Section 6 (table 6): marked as not page content in the UI  — text: Experienced Electrical Repair…; *Insert Icon Here*; *Insert Icon Here*; *Insert Icon Here*; Trusted Experience; Honest Recommendations; Quality Workmanship; For more than two decades, we…; Our technicians explain the i…; Every repair and installation…; *Schedule Service Button*
- Section 7 (table 7): marked as not page content in the UI  — text: Fast Help from an Emergency E…; *Insert Image Here*; Some electrical problems simp…; Burning smells from electrica…; Sparking outlets; Smoke coming from your breake…; Sudden complete power loss af…; Exposed wiring; Electrical damage following s…; Prompt service helps reduce t…; *Get In Touch Button*
- Section 9 (table 9): marked as not page content in the UI  — text: Local Electrical Contractor S…; Albert Services has proudly s…; Because we regularly serve co…; *Insert Image Here*
- Section 11 (table 11): marked as not page content in the UI  — text: Your Trusted Home Service Exp…;  Dayton;  Miamisburg;  Bellbrook;  Riverside;  Centerville;  Springboro;  Oakwood;  Huber Heights;  Kettering;  Beavercreek;  West Carrollton
- Section 12 (table 12): marked as not page content in the UI  — text: Frequently Asked Questions; How do I know if I need an el…; If you're experiencing flicke…; When should I call an emergen…; Contact an emergency electric…; Why should I hire a licensed …; A licensed electrician has th…; What does a residential elect…; A residential electrician han…; How do I know if I need an el…; If you're experiencing flicke…
- Section 13 (table 13): marked as not page content in the UI  — text: Need Reliable Home Service Yo…; *Insert Image Here*; Whether you're dealing with a…; Request A Free Estimate; Call Button; *Insert Contact Form Here*
- Section 14 (table 14): marked as not page content in the UI  — text: *Insert Client Logo*; Quick Links; Services; Useful Links; Contact Information; *Insert Tagline*; Home; About; Specials; Financing; Heating; Cooling Plumbing

### Source placeholders (instructions, no content to map)

- Section 0: '*Schedule Online Button*'
- Section 0: '*Call Button*'
- Section 2: '*Insert Contact Form Here*'
- Section 3: '*Insert Image Here*'
- Section 3: '*Insert Image Here*'
- Section 3: '*Insert Image Here*'
- Section 3: '*Insert Image Here*'
- Section 3: '*Insert Image Here*'
- Section 3: '*Insert Image Here*'
- Section 4: '*Insert Case Studies Here*'
- Section 5: '*Insert Image Here*'
- Section 6: '*Insert Icon Here*'
- Section 6: '*Insert Icon Here*'
- Section 6: '*Insert Icon Here*'
- Section 6: '*Schedule Service Button*'
- Section 7: '*Insert Image Here*'
- Section 7: '*Get In Touch Button*'
- Section 8: '*Insert Image Here*'
- Section 9: '*Insert Image Here*'
- Section 13: '*Insert Image Here*'
- Section 13: '*Insert Contact Form Here*'
- Section 14: '*Insert Client Logo*'
- Section 14: '*Insert Tagline*'
- Section 14: '*Insert Contact Details*'
- Section 14: '[Social Media Buttons]'

### Document notes (header/footer text, not page content)

- Disclaimer: Please note that this content has been proofread manually and through grammar checkers to eliminate all spacing errors. Any spacing errors you may come across are due to compatibility issues in Microsoft Word.

## 3. Template fields retained (no source value)

| Element | Widget.field | Current value | Reason |
|---|---|---|---|
| `3e4f198c` | heading.title | Heating | no mapping rule |
| `1ad728c0` | heading.title | Stay Warm with Reliable Heating Services in Bellbrook | no mapping rule |
| `19602cd3` | template.template_id | global template #422 | global Elementor template - content lives outside this JSON |
| `e5342d8` | call-to-action.title | Heating Repair | no mapping rule |
| `e5342d8` | call-to-action.description | If your furnace or heating system isn't producing enough heat, is making unusual noises, … | no mapping rule |
| `e5342d8` | call-to-action.button | Book Now | no mapping rule |
| `2e867c8b` | call-to-action.title | Heating Installation & Replacement | no mapping rule |
| `2e867c8b` | call-to-action.description | When it's time for a new system, we'll help you choose an energy-efficient heating soluti… | no mapping rule |
| `2e867c8b` | call-to-action.button | Book Now | no mapping rule |
| `5526e620` | call-to-action.title | Heating Maintenance | no mapping rule |
| `5526e620` | call-to-action.description | Routine heating maintenance helps improve efficiency, extend equipment life, and reduce t… | no mapping rule |
| `5526e620` | call-to-action.button | Book Now | no mapping rule |
| `918548c` | call-to-action.title | Heat Pump Services | no mapping rule |
| `918548c` | call-to-action.description | We install, repair, and maintain heat pumps to provide dependable year-round comfort and … | no mapping rule |
| `918548c` | call-to-action.button | Book Now | no mapping rule |
| `7ca18942` | call-to-action.title | Thermostat Services | no mapping rule |
| `7ca18942` | call-to-action.description | Smart thermostat upgrades and calibrations help improve comfort while giving homeowners g… | no mapping rule |
| `7ca18942` | call-to-action.button | Book Now | no mapping rule |
| `78eb9414` | call-to-action.title | Emergency Heating Repairs | no mapping rule |
| `78eb9414` | call-to-action.description | Heating problems don't always happen during business hours. Our team responds quickly to … | no mapping rule |
| `78eb9414` | call-to-action.button | Book Now | no mapping rule |
| `56db65e2` | heading.title | Experienced Heating Professionals You Can Trust | no mapping rule |
| `74d0cc6c` | image-box.title_text | Fast Response | no mapping rule |
| `74d0cc6c` | image-box.description_text | When your heating system stops working, our team responds quickly to diagnose the issue a… | no mapping rule |
| `748ac504` | image-box.title_text | Skilled Professionals | no mapping rule |
| `748ac504` | image-box.description_text | Every local heating technician on our team is trained to identify problems accurately and… | no mapping rule |
| `2cf86f1e` | image-box.title_text | Honest Recommendations | no mapping rule |
| `2cf86f1e` | image-box.description_text | We explain every repair clearly, answer your questions, and help you make informed decisi… | no mapping rule |
| `3fe535e3` | button.text | Schedule Service | no mapping rule |
| `17871ff0` | heading.title | Serving the Bellbrook Community | no mapping rule |
| `26377df3` | heading.title | The Benefits of Regular Heating Maintenance | no mapping rule |
| `88f074a` | text-editor.editor | Routine heating maintenance is one of the smartest investments you can make for your home… | no mapping rule |
| `7094982a` | heading.title | Expert Heating Installation and Replacement | no mapping rule |
| `55033ecf` | text-editor.editor | If your heating system is older, requires frequent repairs, or no longer keeps your home … | no mapping rule |
| `6472341` | heading.title | Why Homeowners Choose Albert Services | no mapping rule |
| `50d6e8f4` | image-box.title_text | Experienced Team | no mapping rule |
| `50d6e8f4` | image-box.description_text | Our knowledgeable technicians have decades of experience providing dependable heating sol… | no mapping rule |
| `1605eef` | image-box.title_text | Honest Service | no mapping rule |
| `1605eef` | image-box.description_text | We believe in transparent recommendations and clear communication from start to finish. | no mapping rule |
| `42fdedf9` | image-box.title_text | Dependable Scheduling and 30-minute Arrival Window | no mapping rule |
| `42fdedf9` | image-box.description_text | We respect your time. Instead of asking you to wait around all day, we provide a convenie… | no mapping rule |
| `7389db81` | image-box.title_text | Quality Workmanship | no mapping rule |
| `7389db81` | image-box.description_text | Every repair and installation is completed with attention to detail and lasting quality. | no mapping rule |
| `7494fae5` | image-box.title_text | Customer Satisfaction | no mapping rule |
| `7494fae5` | image-box.description_text | Your comfort is always our highest priority. | no mapping rule |
| `30fc22d5` | image-box.title_text | Local Expertise | no mapping rule |
| `30fc22d5` | image-box.description_text | As experienced heating and cooling contractors, we understand the heating needs of Dayton… | no mapping rule |
| `155ae91c` | heading.title | What Our Client Says | no mapping rule |
| `2743f7a9` | shortcode.shortcode | [trustindex no-registration=google] | no mapping rule |
| `1a652e61` | template.template_id | global template #449 | global Elementor template - content lives outside this JSON |
| `46239fd6` | heading.title | FAQ | no mapping rule |
| `1dcb8196` | heading.title | Frequently Asked Questions | no mapping rule |
| `20c5a18b` | nested-accordion.items | (accordion untouched) | no mapping rule |
| `7b86e625` | text-editor.editor | Most manufacturers recommend professional heating maintenance once each year before the h… | no mapping rule |
| `66cec799` | text-editor.editor | Signs include inconsistent temperatures, unusual noises, weak airflow, higher energy bill… | no mapping rule |
| `7256f716` | text-editor.editor | If your system is more than 15–20 years old, requires frequent repairs, or struggles to k… | no mapping rule |
| `43f7f1e5` | text-editor.editor | Yes. Our experienced technicians work on many types of residential heating equipment and … | no mapping rule |
| `10a269fc` | heading.title | Need Reliable Home Service You Can Count On? | no mapping rule |

### Media retained from template (source only has placeholders)

- `e5342d8` call-to-action `content[2].elements[2].elements[0]` url=(empty) alt=''
- `2e867c8b` call-to-action `content[2].elements[2].elements[1]` url=(empty) alt=''
- `5526e620` call-to-action `content[2].elements[2].elements[2]` url=(empty) alt=''
- `918548c` call-to-action `content[2].elements[2].elements[3]` url=(empty) alt=''
- `7ca18942` call-to-action `content[2].elements[2].elements[4]` url=(empty) alt=''
- `78eb9414` call-to-action `content[2].elements[2].elements[5]` url=(empty) alt=''
- `75f9d86f` image `content[3].elements[1].elements[0]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/09/expert-heating-services-in-bellbrook-oh.jpg alt=''
- `74d0cc6c` image-box `content[4].elements[1].elements[0]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/08/ab-icons-2.png alt=''
- `748ac504` image-box `content[4].elements[1].elements[1]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/08/ab-icons-1.png alt=''
- `2cf86f1e` image-box `content[4].elements[1].elements[2]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/08/sec-icons-3.png alt=''
- `1f15c5e7` image `content[5].elements[1].elements[0]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/08/ab-2.webp alt=''
- `6cfe06eb` image `content[6].elements[1].elements[0]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/09/professional-heating-services-in-bellbrook-oh.jpg alt=''
- `26c5c78` image `content[7].elements[1].elements[0]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/09/trusted-heating-services-in-bellbrook-oh.jpg alt=''
- `50d6e8f4` image-box `content[8].elements[0].elements[1].elements[0]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/08/ab-icons-1.png alt=''
- `1605eef` image-box `content[8].elements[0].elements[1].elements[1]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/08/sec-icons-3.png alt=''
- `42fdedf9` image-box `content[8].elements[0].elements[1].elements[2]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/08/Group-1261158417.png alt=''
- `7389db81` image-box `content[8].elements[0].elements[1].elements[3]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/08/Group-1261158420.png alt=''
- `7494fae5` image-box `content[8].elements[0].elements[1].elements[4]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/08/sec-icons-5.png alt=''
- `30fc22d5` image-box `content[8].elements[0].elements[1].elements[5]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/08/loc-img.png alt=''
- `4f004f1d` image `content[12].elements[1].elements[0]` url=https://mb.dev-version.com/alberthvac/wp-content/uploads/2026/09/cta-img1.webp alt=''

## 4. Warnings / ambiguities

None.

## 5. Validation

- ✅ JSON serialises and re-parses
- ✅ Template structure, key names and data types preserved
- ✅ New elements exist only as logged clones - 0 clone(s) logged
- ✅ Element ids unique - 89 elements
- ✅ Accordion items match child containers
- ✅ No relevant source node silently skipped - 1 unmapped section(s), 5 unmapped node(s) in mapped sections - all reported
- ✅ No source node mapped to two different targets
- ✅ Every mapped text appears verbatim in its target field
- ✅ Source wording unmodified (spot check on whole output)
- ✅ No stale template terms left in text fields - terms checked: []
