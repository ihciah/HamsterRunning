package main

import (
	"github.com/influxdata/influxdb/client/v2"
	"gobot.io/x/gobot"
	"gobot.io/x/gobot/drivers/gpio"
	"gobot.io/x/gobot/platforms/raspi"
	"log"
	"time"
)

const (
	chanBufSize   = 1024
	writeInterval = 60
	dbAddr        = "http://127.0.0.1:8086"
	dbName        = "hamster"
	dbUserName    = "admin"
	dbPassword    = ""
)

func gpioReader() {
	queue := make(chan time.Time, chanBufSize)
	go dbWriter(queue)

	r := raspi.NewAdaptor()
	button := gpio.NewButtonDriver(r, "3")
	work := func() {
		button.On(gpio.ButtonPush, func(data interface{}) {
			log.Printf("A round.")
			queue <- time.Now()
		})
	}
	robot := gobot.NewRobot("buttonBot",
		[]gobot.Connection{r},
		[]gobot.Device{button},
		work,
	)
	robot.Start()
}

func dbWriter(signal chan time.Time) {
	conn, err := client.NewHTTPClient(client.HTTPConfig{
		Addr:     dbAddr,
		Username: dbUserName,
		Password: dbPassword,
	})
	if err != nil {
		log.Printf("Can not connect database: %s", err)
	}

	for {
		bp, err := client.NewBatchPoints(client.BatchPointsConfig{
			Database:  dbName,
			Precision: "us",
		})
		if err != nil {
			log.Printf("Can not create batch points: %s", err)
			continue
		}

		trigger := time.After(writeInterval * time.Second)
		for exit := false; !exit; {
			select {
			case <-trigger:
				if len(bp.Points()) == 0 {
					log.Printf("No points to submit.")
					exit = true
					continue
				}
				if err := conn.Write(bp); err != nil {
					log.Printf("Can not write data to server: %s", err)
				}
				log.Printf("Batch points added.")
				exit = true
				continue
			case t := <-signal:
				fields := map[string]interface{}{
					"round": 1,
				}
				pt, err := client.NewPoint("round", map[string]string{}, fields, t)
				if err == nil {
					log.Printf("Point created.")
					bp.AddPoint(pt)
					log.Printf("Point added.")
				} else {
					log.Printf("Can not create point: %s", err)
				}
			}
		}
	}
}

func main() {
	gpioReader()
}
