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

// func init() {
//   var err error
//   client, err = storage.NewClient(context.Background())
//   if err != nil {
//     log.Fatalf("storage.NewClient: %v", err)
//   }
// }

func make(ctx context.Context, e event.Event) error {
  log.Printf("Event ID: %s", e.ID())
  log.Printf("Event Type: %s", e.Type())

  var data StorageObjectData
  if err := e.DataAs(&data); err != nil {
    return fmt.Errorf("event.DataAs: %v", err)
  }
  log.Printf("Bucket: %s", data.Bucket)
  log.Printf("File: %s", data.Name)
  log.Printf("Metageneration: %d", data.Metageneration)
  log.Printf("Created: %s", data.TimeCreated)
  log.Printf("Updated: %s", data.Updated)

  inputBlob := client.Bucket(data.Bucket).Object(data.Name)
  // outputBlob := client.Bucket(destination).Object(data.Name)
  // if outputBlob {
  //   return fmt.Errorf("Blob already exist")
  // }

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

  outputBlob := client.Bucket(destination).Object(data.Name)
  w := outputBlob.If(storage.Conditions{DoesNotExist: true}).NewWriter(ctx)
  defer w.Close()

  var opts jpeg.Options
	opts.Quality = quality
  err = jpeg.Encode(w, newImage, &opts)
	if err != nil {
		return fmt.Errorf("Bucket writer: %v", err)
	}

	return nil
}
