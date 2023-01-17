package main

import (
	"context"
	"fmt"
	"image"
	"image/jpeg"
	"log"
	"time"

	"cloud.google.com/go/storage"
	"github.com/cloudevents/sdk-go/v2/event"
	"github.com/nfnt/resize"
)

const size = 400
const quality = 85
const destination = "thumbnails400"

type StorageObjectData struct {
  Bucket         string    `json:"bucket,omitempty"`
  Name           string    `json:"name,omitempty"`
  Metageneration int64     `json:"metageneration,string,omitempty"`
  TimeCreated    time.Time `json:"timeCreated,omitempty"`
  Updated        time.Time `json:"updated,omitempty"`
}

var client *storage.Client

func init() {
  var err error
  client, err = storage.NewClient(context.Background())
  if err != nil {
    log.Fatalf("storage.NewClient: %v", err)
  }
}

func eventData(e event.Event) StorageObjectData {
  log.Printf("Event ID: %s", e.ID())
  log.Printf("Event Type: %s", e.Type())

  var data StorageObjectData
  if err := e.DataAs(&data); err != nil {
    log.Printf("event.DataAs: %v", err)
  }
  log.Printf("Bucket: %s", data.Bucket)
  log.Printf("File: %s", data.Name)
  log.Printf("Metageneration: %d", data.Metageneration)
  log.Printf("Created: %s", data.TimeCreated)
  log.Printf("Updated: %s", data.Updated)

  return data

}

func make(ctx context.Context, e event.Event) error {
  data := eventData(e)
  inputBlob := client.Bucket(data.Bucket).Object(data.Name)

  r, err := inputBlob.NewReader(ctx)
	if err != nil {
		return fmt.Errorf("Bucket reader: %v", err)
	}

  im, _, err := image.DecodeConfig(r)
  if err != nil {
    return fmt.Errorf("DecodeConfig image: %v", err)
  }
  log.Printf("Width, Height: %v, %v", im.Width, im.Height)

  img, _, err := image.Decode(r)
  if err != nil {
		return fmt.Errorf("Decode image: %v", err)
	}

  var newImage image.Image
	if im.Width >= im.Height {
		newImage = resize.Resize(size, 0, img, resize.Lanczos3)
	} else {
		newImage = resize.Resize(0, size, img, resize.Lanczos3)
	}

  var opts jpeg.Options
	opts.Quality = quality

  outputBlob := client.Bucket(destination).Object(data.Name)
  w := outputBlob.If(storage.Conditions{DoesNotExist: true}).NewWriter(ctx)
  // defer w.Close()

  err = jpeg.Encode(w, newImage, &opts)
	if err != nil {
		return fmt.Errorf("jpeg.Encode: %v", err)
	}
  if err := w.Close(); err != nil {
    return fmt.Errorf("Bucket writer: %v", err)
  }

	return nil
}

func remove(ctx context.Context, e event.Event) error {
  data := eventData(e)
  blob := client.Bucket(destination).Object(data.Name)
  if err := blob.Delete(ctx); err != nil {
    return fmt.Errorf("Bucket delete: %v", err)
  }
  return nil
}

/*
gcloud functions deploy gothumb \
--gen2 \
--runtime=go119 \
--region=us-central1 \
--source=. \
--entry-point=make \
--trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
--trigger-event-filters="bucket=andsnews.appspot.com"

gcloud functions deploy gothumb \
--gen2 \
--runtime=us-central1 \
--region=REGION \
--source=. \
--entry-point=remove \
--trigger-event-filters="type=google.cloud.storage.object.v1.deleted" \
--trigger-event-filters="bucket=andsnews.appspot.com"
*/
