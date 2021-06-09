const CosmosClient = require("@azure/cosmos").CosmosClient;
const loadIniFile = require('read-ini-file')
const path = require('path')
var XMLHttpRequest = require("xmlhttprequest").XMLHttpRequest;

const fixture = path.join(__dirname, '../keys.ini')
const keys = loadIniFile.sync(fixture)

process.env.NODE_TLS_REJECT_UNAUTHORIZED = "0";
const client = new CosmosClient({ endpoint: keys.cosmosEndpoint, key: keys.cosmosKey,});

const databaseId = keys.cosmosDbID
const containerId = keys.cosmosCntID

const db = client.database(databaseId);
const container = db.container(containerId);

module.exports = async function (context, myTimer) {
    var timeStamp = new Date().toISOString();
    
    const { resources } = await container.items.query("SELECT c.username, count(c.username) from c group by c.username").fetchAll();
    
    resources.map(function(res1){
        res1["count"] = res1["$1"]
        delete res1["$1"]
    })

    for (const eq of resources) 
    {
        equations.push({username: eq.username, count: eq.count})
    }

    var xhr = new XMLHttpRequest();
    xhr.open("POST", yourUrl, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    
    xhr.send(JSON.stringify({
        users: equations
    }));

    if (myTimer.isPastDue)
    {
        context.log('JavaScript is running late!');
    }
    context.log('JavaScript timer trigger function runs every 30 seconds.', timeStamp);   
};
