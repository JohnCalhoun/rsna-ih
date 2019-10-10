var aws=require('aws-sdk')
var s3=new aws.S3()
var _=require('lodash')

exports.handler=function(event,context,callback){
    console.log(JSON.stringify(event,null,2))
    try{
        var channels=event.params.channels
        var out=Object.keys(channels).map(function(key){
            var channel=channels[key]
            var out=Object.assign({
              "ChannelName":key, 
              "DataSource": { 
                "S3DataSource": Object.assign({ 
                  "S3DataType": channel.type || "S3Prefix", 
                  "S3Uri":channel.uri || `s3://${event.params.databucket}/${channel.path}`, 
                  "S3DataDistributionType": channel.dist ? "ShardedByS3Key"  : "FullyReplicated",
                },_.pick(channel,["AttributeNames"]))
              },
              "InputMode":channel.InputMode || "File",
              "CompressionType": "None",
              "RecordWrapperType": "None"
            },
            _.pick(channel,["ShuffleConfig","RecordWrapperType","ContentType","ContentType"])
            )
            if(channels[key].contentType){
                out.ContentType=channels[key].contentType
            }
            return out
        })
        if(out.length){
            event.args.training.InputDataConfig=out
        }else{
            delete event.args.training.InputDataConfig
        }
        callback(null,event.args.training)
    }catch(e){
        console.log(e)
        callback(new Error(e))
    }
}
