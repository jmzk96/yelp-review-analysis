drop table CLUSTER_WEATHER;

/*==============================================================*/
/* Table: CLUSTER_WEATHER                                       */
/*==============================================================*/
create table CLUSTER_WEATHER (
   CLUSTERID            INT4                 not null,
   DATE                 DATE                 not null,
   TMAX                 DECIMAL(6,2)         null,
   TMIN                 DECIMAL(6,2)         null,
   PERCEPTION           DECIMAL(10,2)        null,
   SNOW                 DECIMAL(10,2)        null,
   SNOWDEPTH            DECIMAL(10,2)        null,
   constraint PK_CLUSTER_WEATHER primary key (CLUSTERID, DATE)
);

alter table CLUSTER_WEATHER
   add constraint FK_CLUSTER__REFERENCE_CLUSTER foreign key (CLUSTERID)
      references CLUSTER (CLUSTERID)
      on delete restrict on update restrict;