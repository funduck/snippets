const cluster = require('cluster')
cluster.schedulingPolicy = cluster.SCHED_RR
const http = require('http')
const numCPUs = require('os').cpus().length

if (cluster.isMaster) {
  console.log(`Master ${process.pid} is running`)

  // Fork workers.
  for (let i = 0; i < numCPUs; i++) {
    const worker = cluster.fork()
    for (const event of ['listening', 'disconnect', 'exit', 'error']) {
      worker.on(event, (args) => {
        console.log(`Master: Worker ${worker.id} received event ${event} ${JSON.stringify(args || null)}`)
      })
    }
  }

  cluster.on('exit', (worker, code, signal) => {
    console.log(`Master: worker ${worker.id} died`)
  })

  cluster.on('online', (worker) => {
    console.log(`Master: worker ${worker.id} is online`)
    worker.send(`Hello ${worker.id}`)
  })

  cluster.on('message', (worker, message) => {
    console.log(`Master: worker ${worker.id} send me ${message}`)
  })

  function shutdown (signal) {
    console.log(`Master: Received exit signal ${signal} terminating`)
    cluster.disconnect(() => { process.exit(signal) })
  }

  for (const s of ['SIGTERM', 'SIGINT']) {
    process.on(s, shutdown)
  }
} else {
  // Workers can share any TCP connection
  // In this case it is an HTTP server
  http.createServer((req, res) => {
    console.log(`Worker ${cluster.worker.id} accepted connection`)
    let timer = setTimeout(() => {
      timer = 0
      res.writeHead(200)
      const id = process.hrtime.bigint()
      console.log(`Worker ${cluster.worker.id} responds ${id}`)
      res.end(`hello world ${id}\n`)
      cluster.worker.send(`Responded to ${id}`)
    }, 3000)
    req.on('close', () => {
      if (timer) {
        clearTimeout(timer)
      }
    })
  }).listen(8000)

  console.log(`Worker ${cluster.worker.id} started`)

  for (const event of ['message', 'exit']) {
    cluster.worker.on(event, (args) => {
      console.log(`Worker ${cluster.worker.id} received event ${event} ${args}`)
    })
  }
}
