var fs=require('fs')
var _=require('lodash')

module.exports={
  "Parameters":{
    "AssetBucket":{"Type":"String"},
    "AssetPrefix":{"Type":"String"},
  },
  "Conditions":{},
  "Outputs":{},
  "Resources":Object.assign(
    require('./cfn'),
    require('./lambda')
  ),
  "AWSTemplateFormatVersion": "2010-09-09",
  "Description": "Automates the building and deployment of SageMaker custom models using StepFunctions and CodeBuild",
}


