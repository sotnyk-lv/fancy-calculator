const {ServiceBusClient} = require("@azure/service-bus");
const CosmosClient = require("@azure/cosmos").CosmosClient;
const { v4: uuidv4 } = require('uuid');
const loadIniFile = require('read-ini-file')
const path = require('path')

const fixture = path.join(__dirname, 'keys.ini')
const keys = loadIniFile.sync(fixture)

const port = process.env.PORT || 80;

const connStr = "Endpoint=sb://ucu-servise-bus.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;" + keys.sbConnectionStr
const qName = keys.sbQueueName

process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";

const client = new CosmosClient({ endpoint: keys.cosmosEndpoint, key: keys.cosmosKey,});

const databaseId = keys.cosmosDbID
const containerId = keys.cosmosCntID

const db = client.database(databaseId);
const container = db.container(containerId);

async function main(){
    const sbClient = new ServiceBusClient(connStr);
    const receiver = sbClient.createReceiver(qName);

    const msgHandler = async (msg) => {
        console.log(msg.body);
        
        var equation = msg.body;
        equation.id = uuidv4();
        container.items.create(equation);
    }

    const errHandler = async (err) => {
        console.log(err);
    }

    receiver.subscribe({
        processMessage: msgHandler,
        processError: errHandler
    });
}

main().catch((err) => {
    console.log("Error: ", err);
    process.exit(1);
})
