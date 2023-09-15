ALTER TABLE cluster add clustername varchar(50)

UPDATE cluster set clustername = 'Phoenix' where clusterid = 1;
UPDATE cluster set clustername = 'Cleveland' where clusterid = 2;
UPDATE cluster set clustername = 'Calgary' where clusterid = 3;
UPDATE cluster set clustername = 'Montreal' where clusterid = 4;
UPDATE cluster set clustername = 'Charlotte' where clusterid = 5;
UPDATE cluster set clustername = 'Las Vegas' where clusterid = 6;
UPDATE cluster set clustername = 'Madison' where clusterid = 7;
UPDATE cluster set clustername = 'Missisauga' where clusterid = 8;
UPDATE cluster set clustername = 'Pittsburgh' where clusterid = 9;
UPDATE cluster set clustername = 'Champaign' where clusterid = 10;