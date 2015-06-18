var Q = require('q');

module.exports = {
  status: function() {
    return Q.resolve({'status': 'CLOUDY'});
  },
  services: function() {
    return Q.resolve([
      {"description": "IAAS", "name": "IAAS", "status": "CLOUDY"},
      {"description": "PAAS", "name": "PAAS", "status": "SUNNY"},
      {"description": "Site", "name": "Site", "status": "STORMY"},
      {"description": "API", "name": "API", "status": "SUNNY"},
      {"description": "SSL", "name": "SSL", "status": "SUNNY"},
      {"description": "Domain", "name": "Domain", "status": "SUNNY"},
      {"description": "Email", "name": "Email", "status": "SUNNY"}
    ]);
  },
  events: function() {
    return Q.resolve([
      {"category": "Maintenance", "date_end": "2014-10-16T17:51:14+00:00", "date_start": "2014-10-16T17:00:49+00:00", "duration": 100, "estimate_date_end": "2014-10-16T17:45:14+00:00", "id": 4, "services": ["Site", "API"], "title": "truc"}, 
      {"category": "Maintenance", "date_end": "2014-10-11T13:51:14+00:00", "date_start": "2014-10-11T12:10:49+00:00", "duration": 100, "estimate_date_end": "2014-10-11T13:51:14+00:00", "id": 3, "services": ["Site", "API"], "title": "truc"}, 
      {"category": "Maintenance", "date_end": "2014-10-11T12:50:31+00:00", "date_start": "2014-10-11T11:50:17+00:00", "duration": 60, "estimate_date_end": "2014-10-11T12:50:31+00:00", "id": 2, "services": ["IAAS"], "title": "machin"},
      {"category": "Incident", "date_end": "2014-10-04T17:29:59+00:00", "date_start": "2014-10-04T14:29:59+00:00", "duration": 180, "estimate_date_end": "2014-10-05T00:29:59+00:00", "id": 1, "services": ["Site", "SSL"], "title": "asdasd"}
    ]);
  },
  event: function(id) {
    switch(id) {
      case '1':
        return Q.resolve(
          {"category": "Incident", "date_end": "2014-10-04T17:29:59+00:00", "date_start": "2014-10-04T14:29:59+00:00", "duration": 180, "estimate_date_end": "2014-10-05T00:29:59+00:00", "id": 1, "logs": [], "services": ["Site", "SSL"], "summary": "# asdasd\r\n\r\ncoucou\r\n\r\n## coucou2\r\n \r\n`coucou`\r\n\r\n# coucou3\r\n\r\ncoucou ca va?\r\n\r\nparce que sinon\r\n\r\n", "title": "asdasd"}
        );
      case '2':
        return Q.resolve(
          {"category": "Maintenance", "date_end": "2014-10-11T12:50:31+00:00", "date_start": "2014-10-11T11:50:17+00:00", "duration": 60, "estimate_date_end": "2014-10-11T12:50:31+00:00", "id": 2, "logs": [], "services": ["IAAS"], "summary": "", "title": "machin"}
        );
      case '3':
        return Q.resolve(
          {"category": "Maintenance", "date_end": "2014-10-11T13:51:14+00:00", "date_start": "2014-10-11T12:10:49+00:00", "duration": 100, "estimate_date_end": "2014-10-11T13:51:14+00:00", "id": 3, "logs": [], "services": ["Site", "API"], "summary": "# h1\r\n\r\ntruc \r\n\r\n## h2\r\n\r\nalsdkjs\r\n\r\nalskjdlk\r\n\r\n### h3\r\n\r\n#### h4\r\n \r\n##### h5\r\n \r\n###### h6\r\n\r\n * foo\r\n * bar\r\n\r\n \r\n`code goes here`\r\n\r\n*italic*\r\n**bold**\r\n\r\n\r\nvery\r\n\r\nvery\r\n\r\nvery\r\nvery\r\n\r\nvery\r\n\r\nvery\r\nvery\r\n\r\nvery\r\n\r\nvery\r\nvery\r\n\r\nvery\r\n\r\nvery\r\nvery\r\n\r\nvery\r\n\r\nvery\r\n\r\n", "title": "truc"}
        );
      case '4':
        return Q.resolve(
          {"category": "Maintenance", "date_end": "2014-10-16T17:51:14+00:00", "date_start": "2014-10-17T17:00:49+00:00", "duration": 100, "estimate_date_end": "2014-10-17T17:45:14+00:00", "id": 3, "logs": [], "services": ["Site", "API"], "summary": "# h1\r\n\r\ntruc \r\n\r\n## h2\r\n\r\nalsdkjs\r\n\r\nalskjdlk\r\n\r\n### h3\r\n\r\n#### h4\r\n \r\n##### h5\r\n \r\n###### h6\r\n\r\n * foo\r\n * bar\r\n\r\n \r\n`code goes here`\r\n\r\n*italic*\r\n**bold**\r\n\r\n\r\nvery\r\n\r\nvery\r\n\r\nvery\r\nvery\r\n\r\nvery\r\n\r\nvery\r\nvery\r\n\r\nvery\r\n\r\nvery\r\nvery\r\n\r\nvery\r\n\r\nvery\r\nvery\r\n\r\nvery\r\n\r\nvery\r\n\r\n", "title": "truc"}
        );
       default:
        return Q.reject("");
    }
  },
}
