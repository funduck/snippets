const express = require('express')

const taskCancels = new Set()

async function startServer () {
  const app = express()
  app.get('/', (req, res) => {
    res.send('Hello World!')
  })
  const port = 8888
  const server = app.listen(port, () => {
    console.log(`Example app listening on port ${port}`)
  })
  taskCancels.add(() => {
    console.log('Cancel received, "server" is closing')
    server.close()
  })
}

async function startWorker () {
  let ok = true
  taskCancels.add(() => {
    console.log('Cancel "doing"')
    ok = false
  })
  while (ok) {
    console.log('doing')
    await new Promise((resolve) => { setTimeout(resolve, 1000) })
  }
}

function run () {
  Promise.allSettled([startServer(), startWorker()])
    .then(() => {
      console.log('All tasks done')
    })
    .catch((e) => {
      console.error(e)
    })
}

function shutdown (signal) {
  console.log(`Received exit signal ${signal} terminating`)
  for (const cancel of taskCancels) {
    cancel()
  }
}

for (const s of ['SIGTERM', 'SIGINT']) {
  process.on(s, shutdown)
}

run()
