# nuclia.plone

![Nuclia logo](https://nuclia.cloud/assets/logos/logo_text.svg)

This Plone add-on allows to index Plone contents in [Nuclia](https://nuclia.com/).

## Create a Nuclia knowledge box

[Create a Nuclia account](https://docs.nuclia.dev/docs/quick-start/create)

## Install the add-on

Add `nuclia.plone` in your buildout in the `eggs` section and run buildout.

Restart Plone.

Go to Site Setup / Add-ons and install `nuclia.plone`.

Go to Nuclia settings, and enter the following:

- Knowledge box ID: you have a default knowledge box created with your Nuclia account, go to [Nuclia dashboard](https://nuclia.cloud/), the knowledge box ID is indicated on the home page in the **Nuclia APi endpoint**.
- API key: see [how to get an API key](https://docs.nuclia.dev/docs/guides/getting-started/quick-start/push#get-an-api-key).
- Region: this the geographical region your knowledge box is attached to.
- Widget snippet: see [how to create a widget](https://docs.nuclia.dev/docs/guides/getting-started/quick-start/search#add-a-search-widget-to-your-website).
- File attribute: the attribute of the content that contains the file to index. Default is `file`.
- Metadata mapping: Nuclia allows to store the following metadata: `title`, `summary`, `tags`, `contributors`, `created`, `modified`. You can map Plone content fields to these metadata fields. If the field belongs to the parent node, use the following format: `parent/field_name`.
- Workflow states: you can choose which workflow states trigger indexing in Nuclia. Default is `published`.

## Usage

Everytime a content having a file is created or modified (and if it is in the appropriate workflow state).

The Nuclia search widget is visible on the `/@@nuclia-search` view.
