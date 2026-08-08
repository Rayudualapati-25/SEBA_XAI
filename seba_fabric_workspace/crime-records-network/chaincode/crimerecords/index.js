'use strict';

const RecordContract = require('./lib/recordContract');
const AccessContract = require('./lib/accessContract');
const AuditContract = require('./lib/auditContract');

module.exports.RecordContract = RecordContract;
module.exports.AccessContract = AccessContract;
module.exports.AuditContract = AuditContract;
module.exports.contracts = [RecordContract, AccessContract, AuditContract];
