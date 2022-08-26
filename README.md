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

- Knowledge box ID: you have a default knowledge box created with your Nuclia account, go to [Nuclia dashboard](https://nuclia.cloud/), the knowledge box ID is indicated on the home page in the **Nuclia APi endpoint**
- API key: see [how to get an API key](https://docs.nuclia.dev/docs/quick-start/push#get-a-service-access-token)
- Region: this the geographical region your knowledge box is attached to (at the moment only `europe-1` is supported)

## Usage

Everytime a `File` or a `Link` content is created, it is indexed in Nuclia.

TODO: display the widget