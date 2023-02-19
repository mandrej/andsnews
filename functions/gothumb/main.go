package gothumb

import (
	"context"
	"fmt"
	"log"
	"os"
	"strconv"
	"time"

	"cloud.google.com/go/storage"
	"github.com/cloudevents/sdk-go/v2/event"
)

const quality = 85
var client *storage.Client
var maxSize uint64
var destination string

type StorageObjectData struct {
  Bucket         string    `json:"bucket,omitempty"`
  Name           string    `json:"name,omitempty"`
  Metageneration int64     `json:"metageneration,string,omitempty"`
  TimeCreated    time.Time `json:"timeCreated,omitempty"`
  Updated        time.Time `json:"updated,omitempty"`
  ContentType    string    `json:"content-type,omitempty"`
}

func init() {
  var err error
  var ok bool

  if client, err = storage.NewClient(context.Background()); err != nil {
    log.Fatalf("storage.NewClient: %v", err)
    os.Exit(1)
  }
  if size, ok := os.LookupEnv("MAX_SIZE"); !ok {
    log.Fatalf("No MAX_SIZE given")
  } else {
    maxSize, _ = strconv.ParseUint(size, 10, 64)
  }
  if destination, ok = os.LookupEnv("THUMBNAILS"); !ok {
    log.Fatalf("No THUMBNAILS given")
    os.Exit(1)
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
  log.Printf("Name: %s", data.Name)
  log.Printf("ContentType: %s", data.ContentType)

  return data
}

func test2(ctx context.Context, e event.Event) error {
  data := eventData(e)
  inputBlob := client.Bucket(data.Bucket).Object(data.Name)
  a, err := inputBlob.Attrs(ctx)
  if err == nil {
    fmt.Printf("inputBlob %v", a)
  } else {
    fmt.Printf("inputBlob error %v", err)
  }
  outputBlob := client.Bucket(destination).Object(data.Name).If(storage.Conditions{DoesNotExist: true})
  b, err := outputBlob.Attrs(ctx)
  if err == nil {
    fmt.Printf("outputBlob %v", b)
  } else {
    fmt.Printf("outputBlob error %v", err)
  }

  // r, err := inputBlob.NewReader(ctx)
	// if err != nil {
	// 	return fmt.Errorf("Bucket reader: %v", err)
	// }

  // im, _, err := image.DecodeConfig(r)
  // if err != nil {
  //   return fmt.Errorf("DecodeConfig image: %v", err)
  // }
  // log.Printf("Width, Height: %v, %v", im.Width, im.Height)

  // img, _, err := image.Decode(r)
  // if err != nil {
	// 	return fmt.Errorf("Decode image: %v", err)
	// }

  // var newImage image.Image
	// if im.Width >= im.Height {
	// 	newImage = resize.Resize(uint(maxSize), 0, img, resize.Lanczos3)
	// } else {
	// 	newImage = resize.Resize(0, uint(maxSize), img, resize.Lanczos3)
	// }

  // var opts jpeg.Options
	// opts.Quality = quality

  // w := outputBlob.If(storage.Conditions{DoesNotExist: true}).NewWriter(ctx)
  // // defer w.Close()

  // err = jpeg.Encode(w, newImage, &opts)
	// if err != nil {
	// 	return fmt.Errorf("jpeg.Encode: %v", err)
	// }
  // if err := w.Close(); err != nil {
  //   return fmt.Errorf("Bucket writer: %v", err)
  // }

	return nil
}

// func remove(ctx context.Context, e event.Event) error {
//   data := eventData(e)
//   blob := client.Bucket(destination).Object(data.Name).If(storage.Conditions{DoesNotExist: false})
//   if err := blob.Delete(ctx); err != nil {
//     return fmt.Errorf("Bucket delete: %v", err)
//   }
//   return nil
// }

/*
cd ~/work/andsnews/functions/thumbnail

gcloud functions deploy test2 \
--gen2 \
--runtime=go119 \
--entry-point="test2" \
--trigger-event-filters="type=google.cloud.storage.object.v1.finalized" \
--trigger-event-filters="bucket=andsnews.appspot.com" \
--set-env-vars="MAX_SIZE=400" \
--set-env-vars="THUMBNAILS=thumbnails400" \
--trigger-location="us" \
--region="us-central1"

gcloud functions deploy remove2 \
--gen2 \
--runtime=go119 \
--entry-point="remove2" \
--trigger-event-filters="type=google.cloud.storage.object.v1.deleted" \
--trigger-event-filters="bucket=andsnews.appspot.com" \
--set-env-vars="THUMBNAILS=thumbnails400" \
--trigger-location="us" \
--region="us-central1"
*/
