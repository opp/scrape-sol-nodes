package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"net/http"
	"os"
	"time"
)

type Result struct {
	Result []RPC
}

type RPC struct {
	RPC any
}

func main() {
	if len(os.Args) <= 2 {
		fmt.Println("incorrect usage")
		os.Exit(-1)
	}

	var jsonFile string = os.Args[1]
	var nodesList string = os.Args[2]

	fJSONFile, err := os.Open(jsonFile)
	if err != nil {
		// fmt.Println(err)
		panic(err)
	}
	defer fJSONFile.Close()

	byteValue, _ := ioutil.ReadAll(fJSONFile)
	var result Result
	json.Unmarshal(byteValue, &result)

	client := &http.Client{
		Timeout: 1 * time.Second,
	}

	var nodeCount int = len(result.Result)

	fNodesList, err := os.OpenFile(nodesList, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		// fmt.Println(err)
		panic(err)
	}
	defer fNodesList.Close()

	for i := 0; i < int(nodeCount); i++ {
		if result.Result[i].RPC != nil {
			var url string = "http://" + result.Result[i].RPC.(string)
			respURL, err := client.Get(url)
			if err != nil {
				continue
			}

			var urlHealth string = url + "/health"
			respURLHealth, _ := client.Get(urlHealth)

			body, _ := ioutil.ReadAll(respURLHealth.Body)
			if string(body) == "behind" || string(body) != "ok" {
				fmt.Printf("[%d/%d] \t %s \t status code: %d \t health: %s\n", i, nodeCount, url, respURL.StatusCode, string(body))
				continue
			}

			fmt.Printf("[%d/%d] \t %s \t status code: %d \t health: %s\n", i, nodeCount, url, respURL.StatusCode, string(body))
			if _, err := fNodesList.WriteString(url + "\n"); err != nil {
				fmt.Println(err)
				continue
			}
		}
	}
}
