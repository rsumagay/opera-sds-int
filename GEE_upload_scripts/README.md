
<!-- Header block for project -->
<hr>

<div align="center">

<h1 align="center">Data Product Uploads to Google Earth Engine</h1>
<!-- ☝️ Replace with your repo name ☝️ -->

</div>

<pre align="center">For uploading data products from large-scale test runs for visualization and inspection in Google Earth Engine (GEE)</pre>
<!-- ☝️ Replace with a single sentence describing the purpose of your repo / proj ☝️ -->

<!-- Header block for project -->

<!-- ☝️ Add badges via: https://shields.io e.g. ![](https://img.shields.io/github/your_chosen_action/your_org/your_repo) ☝️ -->

<!-- ☝️ Screenshot of your software (if applicable) via ![](https://uri-to-your-screenshot) ☝️ -->

<!-- ☝️ Replace with a more detailed description of your repository, including why it was made and whom its intended for.  ☝
[INSERT MORE DETAILED DESCRIPTION OF YOUR REPOSITORY HERE]
-->

<!-- example links>
[INSERT LIST OF IMPORTANT PROJECT / REPO LINKS HERE]
[Website](INSERT WEBSITE LINK HERE) | [Docs/Wiki](INSERT DOCS/WIKI SITE LINK HERE) | [Discussion Board](INSERT DISCUSSION BOARD LINK HERE) | [Issue Tracker](INSERT ISSUE TRACKER LINK HERE)
-->

## Features

* Generates a GEE-compatible GeoTIFF of the data products for RTC-S1 and CSLC-S1 (DSWx-HLS products are already GEE-compatible)
* Uploads each GeoTIFF to a Google Cloud Bucket.
  
<!-- ☝️ Replace with a bullet-point list of your features ☝️ -->

## Contents

* [Quick Start](#quick-start)
* [Changelog](#changelog)
* [FAQ](#frequently-asked-questions-faq)
* [Contributing Guide](#contributing)
* [License](#license)
* [Support](#support)

## Quick Start

This guide provides a quick way to get started with our project. Please see our [docs]([INSERT LINK TO DOCS SITE / WIKI HERE]) for a more comprehensive overview.

### Initial instruction from PST

Some things to note about the scripts:
* The main script first finds all sub directories within a specified s3 bucket+prefix. Then, it makes a list of s3 keys that point to the target layer geotifs (e.g. the VH backscatter). It then searches the Google Cloud Storage (GCS) bucket+prefix for cogs that have already been transferred. It compares these lists and creates a list of s3-gcs key pairs that still need to be transferred. Once we have this big list, we iterate through it using multiprocessing and for each pair, download the geotiff (or h5 for cslc), build a GDAL_translate command to translate into a COG of the right format for GEE, and upload to GCS.
* When I ingest the COGs into GEE (after the attached scripts have run completely, I have another set of scripts that performs the ingestion), I need to specify metadata properties for the image. My current workflow just reads these properties from the filename. Most of these are already part of the file name (e.g. polarization, burst ID) but pass direction isn’t so in the upload to GCS step, I read the direction from the file and append A or D to the filename. I do this to save time on the ingestion step where I don’t need to read anything from the COGs themselves.
 
The crux of this conversion is accomplished with gdal_translate CLI commands (passed to the terminal using the subprocess module [in the `processRTC` and `processCSLC` functions, respectively]). These commands are:
* RTC:
  * `gdal_cmd1 = f'gdal_translate -of GTiff -co NBITS=32 {filepath} {tempfile}'`
  * `gdal_cmd2 = f'gdal_translate -of COG -co COMPRESS=DEFLATE -co RESAMPLING=AVERAGE {tempfile} {outfile}'`
* CSLC:
  * `cslc_h5_amp = f'DERIVED_SUBDATASET:AMPLITUDE:NETCDF:"{filepath}":/science/SENTINEL1/CSLC/grids/VV'`
  * `gdal_cmd = f'gdal_translate -of COG -co COMPRESS=DEFLATE -co RESAMPLING=AVERAGE {cslc_h5_amp} {outfile}'`
 
If SDS can run these commands, and include the output with the rest of the product layers, that would be very useful for us. Let me know if you have any questions.


Further Questions & Answers:

1. Question:  Looking at the script code (under `if __name__ == __main__:`), it looks like we will need to update the `s3_prefix` and `gcs_prefix` strings.  Do we need to create a new folder on GCS, or will it autogenerate one based on our string?  It also looks like we should separate the RTC and CSLC products into different directories, or the loops generating the `keyList` entries won’t do the right thing (e.g. pick up the RTC HDF metadata file as potential CSLC products).  Does that sound right?
   - Answer: Yes, the s3_prefix and gcs_prefix need to be updated when pointing these scripts at new runs.
   - Answer: I believe the folder will be auto generated by the GCS prefix you put in.
   - Answer: The script assumes every sub-directory within the s3_prefix contains the files associated with a single product of the same type (RTC or CSLC). It will error if it can’t find the file it is looking for (e.g. if the sub-directory is missing the VH polarization geotif), but has error handling and will continue on to the next key pair. I can’t remember if I made it only print out if there was an error or not.

2. Question: In the `run-translate-RTC-multi.py` script, the code at the end (that calls `run_rtc_transfer()`) is commented out.  Is it safe to uncomment to run the script?
   - Answer: Yes you can uncomment and run. That was only commented out because I just wanted to print number of key pairs last time I ran it
 
3. Question: Do we need any special credentials to for uploading the COGs to Google Cloud?  I didn’t see anything like that in the script, but want to double-check.
   - Answer: You will need to authenticate google command line tools I believe and also have the right privileges for our GCS bucket to write to the bucket. If this is too much of an issue, you can always write these to an AWS s3 bucket instead, and we can handle the transfer (s3 to GCS transfer is very quick and doesn’t require downloading/uploading)



### Requirements

* RTC-S1 or CSLC-S1 products in an S3 bucket.
  
<!-- ☝️ Replace with a numbered list of your requirements, including hardware if applicable ☝️ -->

### Setup Instructions

1. [INSERT STEP-BY-STEP SETUP INSTRUCTIONS HERE, WITH OPTIONAL SCREENSHOTS]
   
<!-- ☝️ Replace with a numbered list of how to set up your software prior to running ☝️ -->

### Run Instructions

1. [INSERT STEP-BY-STEP RUN INSTRUCTIONS HERE, WITH OPTIONAL SCREENSHOTS]

<!-- ☝️ Replace with a numbered list of your run instructions, including expected results ☝️ -->

### Usage Examples

* [INSERT LIST OF COMMON USAGE EXAMPLES HERE, WITH OPTIONAL SCREENSHOTS]

<!-- ☝️ Replace with a list of your usage examples, including screenshots if possible, and link to external documentation for details ☝️ -->

### Build Instructions (if applicable)

1. [INSERT STEP-BY-STEP BUILD INSTRUCTIONS HERE, WITH OPTIONAL SCREENSHOTS]

<!-- ☝️ Replace with a numbered list of your build instructions, including expected results / outputs with optional screenshots ☝️ -->

### Test Instructions (if applicable)

1. [INSERT STEP-BY-STEP TEST INSTRUCTIONS HERE, WITH OPTIONAL SCREENSHOTS]

<!-- ☝️ Replace with a numbered list of your test instructions, including expected results / outputs with optional screenshots ☝️ -->

## Changelog

See our [CHANGELOG.md](CHANGELOG.md) for a history of our changes.

See our [releases page]([INSERT LINK TO YOUR RELEASES PAGE]) for our key versioned releases.

<!-- ☝️ Replace with links to your changelog and releases page ☝️ -->

## Frequently Asked Questions (FAQ)

<!-- example link to FAQ PAGE>
Questions about our project? Please see our: [FAQ]([INSERT LINK TO FAQ / DISCUSSION BOARD])
-->

<!-- example FAQ inline format>
1. Question 1
   - Answer to question 1
2. Question 2
   - Answer to question 2
-->

<!-- example FAQ inline with no questions yet>
No questions yet. Propose a question to be added here by reaching out to our contributors! See support section below.
-->

<!-- ☝️ Replace with a list of frequently asked questions from your project, or post a link to your FAQ on a discussion board ☝️ -->

## Contributing

[INSERT LINK TO CONTRIBUTING GUIDE OR FILL INLINE HERE]
<!-- example link to CONTRIBUTING.md>
Interested in contributing to our project? Please see our: [CONTRIBUTING.md](CONTRIBUTING.md)
-->

<!-- example inline contributing guide>
1. Create an GitHub issue ticket describing what changes you need (e.g. issue-1)
2. [Fork](INSERT LINK TO YOUR REPO FORK PAGE HERE, e.g. https://github.com/my_org/my_repo/fork) this repo
3. Make your modifications in your own fork
4. Make a pull-request in this repo with the code in your fork and tag the repo owner / largest contributor as a reviewer

**Working on your first pull request?** See guide: [How to Contribute to an Open Source Project on GitHub](https://kcd.im/pull-request)
-->

[INSERT LINK TO YOUR CODE_OF_CONDUCT.md OR SHARE TEXT HERE]
<!-- example link to CODE_OF_CONDUCT.md>
For guidance on how to interact with our team, please see our code of conduct located at: [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
-->

<!-- ☝️ Replace with a text describing how people may contribute to your project, or link to your contribution guide directly ☝️ -->

[INSERT LINK TO YOUR GOVERNANCE.md OR SHARE TEXT HERE]
<!-- example link to GOVERNANCE.md>
For guidance on our governance approach, including decision-making process and our various roles, please see our governance model at: [GOVERNANCE.md](GOVERNANCE.md)
-->

## License

See our: [LICENSE](LICENSE)
<!-- ☝️ Replace with the text of your copyright and license, or directly link to your license file ☝️ -->

## Support

[INSERT CONTACT INFORMATION OR PROFILE LINKS TO MAINTAINERS AMONG COMMITTER LIST]

<!-- example list of contacts>
Key points of contact are: [@github-user-1](link to github profile) [@github-user-2](link to github profile)
-->

<!-- ☝️ Replace with the key individuals who should be contacted for questions ☝️ -->




