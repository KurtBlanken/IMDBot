package main

import (
	"github.com/hoisie/web.go"
	"github.com/hoisie/mustache.go"
	"log"
	"fmt"
	"os"
	"os/inotify"
	"io/ioutil"
	"bufio"
	"json"
	"websocket"
	"http"
	"strings"
	"strconv"
)

var templates map [string] *mustache.Template = make(map [string] *mustache.Template)
var in *os.File
var out *os.File

func index(ctx *web.Context) string {
	c := make(map[string]string)
	return templates["www/index.html"].Render(c)
}

func loadTemplates() {
	tables := []string {"www/index.html"}
	for table := range tables {
		t, err := mustache.ParseFile(tables[table])
		if err != nil { log.Fatal(err) }
		templates[tables[table]] = t
	}
}

func templateWatch() {
	watcher, err := inotify.NewWatcher()
	if err != nil { log.Fatal(err) }
	err = watcher.Watch("www")
	if err != nil { log.Fatal(err) }
	for {
    <-watcher.Event
		loadTemplates()
	}
}

func handleWS(ws *websocket.Conn) {
	defer func() { ws.Close() }()
	r := bufio.NewReader(ws)
	s, err := r.ReadString('\n')
	for err == nil {
		var msg map [string] string
		err = json.Unmarshal([]byte(s), &msg)
		if err != nil { log.Println(err); return }
		log.Println(msg["id"] + ": " + msg["msg"])
		_, err = in.WriteString(msg["id"] + "\n")
		if err != nil { log.Println(err); return }
		_, err = in.WriteString(msg["msg"] + "\n")
		if err != nil { log.Println(err); return }
		b := make([]byte, 100000)
		n, err := out.Read(b)
		if err != nil { log.Println(err); return }
		msg["response"] = strings.Trim(string(b[:n]), "\n")
		log.Println(msg["response"])
		b, err = json.Marshal(msg)
		if err != nil { log.Println(err); return }
		ws.Write(b)
		s, err = r.ReadString('\n')
	}
}

func main() {
	pid_file, err := ioutil.ReadFile("/tmp/imdbot_pid")
	if err != nil { log.Fatal(err) }
	pid, err := strconv.Atoi(strings.Trim(string(pid_file), "\n"))
	if err != nil { log.Fatal(err) }
	in, err = os.Open(fmt.Sprintf("/proc/%d/fd/3", pid), os.O_WRONLY|os.O_SYNC, 0)
	if err != nil { log.Fatal(err) }
	out, err = os.Open(fmt.Sprintf("/proc/%d/fd/6", pid), os.O_RDONLY|os.O_SYNC, 0)
	if err != nil { log.Fatal(err) }

	server := new(web.Server)
	server.Config = new(web.ServerConfig)
	server.Config.StaticDir = "www"
	go templateWatch()
	loadTemplates()
	go func() {
		http.Handle("/ws", websocket.Handler(handleWS));
		http.ListenAndServe("0.0.0.0:8081", nil)
	}()
	server.Get("/", index)
  server.Run("0.0.0.0:8080")
}
