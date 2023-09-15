/*==============================================================*/
/* DBMS name:      PostgreSQL 9.x                               */
/* Created on:     21.12.2020 14:47:46                          */
/*==============================================================*/


drop table ATTRIBUTE;

drop index INDEX_BUSINESS_CLUSTERID;

drop table BUSINESS;

drop table CATEGORIES;

drop table CATEGORY;

drop table CHECKINS;

drop table CLUSTER;

drop table CLUSTER_WEATHER;

drop table HOURS;

drop table LOCATION;

drop index INDEX_REVIEWS_BID;

drop index INDEX_REVIEWS_UID;

drop table REVIEWS;

drop table STATIONDATA;

drop index INDEX_TIPS_UID;

drop index INDEX_TIPS_BID;

drop table TIPS;

drop table USERS;

drop table WEATHER;

drop sequence SEQUENCE_1;

drop sequence SEQUENCE_2;

create sequence SEQUENCE_1;

create sequence SEQUENCE_2;

/*==============================================================*/
/* Table: ATTRIBUTE                                             */
/*==============================================================*/
create table ATTRIBUTE (
   ATTR                 VARCHAR(30)          not null,
   BID                  char(22)             not null,
   constraint PK_ATTRIBUTE primary key (ATTR, BID)
);

/*==============================================================*/
/* Table: BUSINESS                                              */
/*==============================================================*/
create table BUSINESS (
   BID                  char(22)             not null,
   CLUSTERID            INT4                 null,
   CITY                 VARCHAR(50)          null,
   STATE                char(3)              null,
   PCODE                VARCHAR(8)           null,
   LON                  DECIMAL(13,10)       not null,
   LAT                  DECIMAL(13,10)       not null,
   STARS                DECIMAL(3,2)         not null,
   REVCOUNT             integer              null,
   NAME                 VARCHAR(100)         null,
   constraint PK_BUSINESS primary key (BID)
);

/*==============================================================*/
/* Index: INDEX_BUSINESS_CLUSTERID                              */
/*==============================================================*/
create  index INDEX_BUSINESS_CLUSTERID on BUSINESS (
CLUSTERID
);

/*==============================================================*/
/* Table: CATEGORIES                                            */
/*==============================================================*/
create table CATEGORIES (
   CID                  integer              not null,
   CAT                  VARCHAR(40)          not null,
   constraint PK_CATEGORIES primary key (CID)
);

/*==============================================================*/
/* Table: CATEGORY                                              */
/*==============================================================*/
create table CATEGORY (
   BID                  char(22)             not null,
   CID                  integer              not null,
   constraint PK_CATEGORY primary key (BID, CID)
);

/*==============================================================*/
/* Table: CHECKINS                                              */
/*==============================================================*/
create table CHECKINS (
   BID                  char(22)             not null,
   DATE                 DATE                 not null,
   AMOUNT               INT4                 null,
   constraint PK_CHECKINS primary key (DATE, BID)
);

/*==============================================================*/
/* Table: CLUSTER                                               */
/*==============================================================*/
create table CLUSTER (
   CLUSTERID            INT4                 not null,
   LON                  DECIMAL(13,10)       null,
   LAT                  DECIMAL(13,10)       null,
   CLUSTERNAME          VARCHAR(50)          null,
   constraint PK_CLUSTER primary key (CLUSTERID)
);

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

/*==============================================================*/
/* Table: HOURS                                                 */
/*==============================================================*/
create table HOURS (
   BID                  char(22)             not null,
   DOW                  integer              not null,
   OPEN                 time                 not null,
   CLOSE                time                 not null,
   constraint PK_HOURS primary key (BID, DOW)
);

/*==============================================================*/
/* Table: LOCATION                                              */
/*==============================================================*/
create table LOCATION (
   SID                  char(11)             not null,
   BID                  char(22)             not null,
   constraint PK_LOCATION primary key (SID, BID)
);

/*==============================================================*/
/* Table: REVIEWS                                               */
/*==============================================================*/
create table REVIEWS (
   RID                  char(22)             not null,
   UID                  char(22)             not null,
   BID                  char(22)             not null,
   STAR                 integer              not null,
   DATE                 date                 not null,
   INTERACTIONS         integer              null,
   TEXT                 TEXT                 null,
   constraint PK_REVIEWS primary key (RID)
);

/*==============================================================*/
/* Index: INDEX_REVIEWS_UID                                     */
/*==============================================================*/
create  index INDEX_REVIEWS_UID on REVIEWS (
UID
);

/*==============================================================*/
/* Index: INDEX_REVIEWS_BID                                     */
/*==============================================================*/
create  index INDEX_REVIEWS_BID on REVIEWS (
BID
);

/*==============================================================*/
/* Table: STATIONDATA                                           */
/*==============================================================*/
create table STATIONDATA (
   SID                  char(11)             not null,
   LON                  DECIMAL(13,10)       not null,
   LAT                  DECIMAL(13,10)       not null,
   ELE                  DECIMAL(8,4)         null,
   STATE                VARCHAR(3)           null,
   NAME                 VARCHAR(35)          null,
   constraint PK_STATIONDATA primary key (SID)
);

/*==============================================================*/
/* Table: TIPS                                                  */
/*==============================================================*/
create table TIPS (
   TID                  char(22)             not null,
   BID                  char(22)             not null,
   UID                  char(22)             not null,
   COMPLIMENTS          integer              null,
   DATE                 date                 not null,
   TEXT                 TEXT                 not null,
   constraint PK_TIPS primary key (TID)
);

/*==============================================================*/
/* Index: INDEX_TIPS_BID                                        */
/*==============================================================*/
create  index INDEX_TIPS_BID on TIPS (
BID
);

/*==============================================================*/
/* Index: INDEX_TIPS_UID                                        */
/*==============================================================*/
create  index INDEX_TIPS_UID on TIPS (
UID
);

/*==============================================================*/
/* Table: USERS                                                 */
/*==============================================================*/
create table USERS (
   UID                  char(22)             not null,
   REVCOUNT             integer              null,
   SINCE                date                 null,
   FRIENDS              integer              null,
   EVALCOUNT            integer              null,
   FANS                 integer              null,
   ELITE                integer              null,
   AVGSTARS             DECIMAL(3,2)         null,
   INTERACTION          integer              null,
   constraint PK_USERS primary key (UID)
);

/*==============================================================*/
/* Table: WEATHER                                               */
/*==============================================================*/
create table WEATHER (
   SID                  char(11)             not null,
   DATE                 date                 not null,
   TMAX                 DECIMAL(6,2)         null,
   TMIN                 DECIMAL(6,2)         null,
   PERCEPTION           DECIMAL(10,2)        null,
   SNOW                 DECIMAL(10,2)        null,
   SNOWDEPTH            DECIMAL(10,2)        null,
   constraint PK_WEATHER primary key (SID, DATE)
);

alter table ATTRIBUTE
   add constraint FK_ATTRIBUT_REFERENCE_BUSINESS foreign key (BID)
      references BUSINESS (BID)
      on delete cascade on update cascade;

alter table BUSINESS
   add constraint FK_BUSINESS_REFERENCE_CLUSTER foreign key (CLUSTERID)
      references CLUSTER (CLUSTERID)
      on delete restrict on update restrict;

alter table CATEGORY
   add constraint FK_CATEGORY_REFERENCE_BUSINESS foreign key (BID)
      references BUSINESS (BID)
      on delete cascade on update cascade;

alter table CATEGORY
   add constraint FK_CATEGORY_REFERENCE_CATEGORI foreign key (CID)
      references CATEGORIES (CID)
      on delete cascade on update cascade;

alter table CHECKINS
   add constraint FK_CHECKINS_REFERENCE_BUSINESS foreign key (BID)
      references BUSINESS (BID)
      on delete cascade on update cascade;

alter table CLUSTER_WEATHER
   add constraint FK_CLUSTER__REFERENCE_CLUSTER foreign key (CLUSTERID)
      references CLUSTER (CLUSTERID)
      on delete restrict on update restrict;

alter table HOURS
   add constraint FK_HOURS_REFERENCE_BUSINESS foreign key (BID)
      references BUSINESS (BID)
      on delete cascade on update cascade;

alter table LOCATION
   add constraint FK_LOCATION_REFERENCE_STATIOND foreign key (SID)
      references STATIONDATA (SID)
      on delete cascade on update cascade;

alter table LOCATION
   add constraint FK_LOCATION_REFERENCE_BUSINESS foreign key (BID)
      references BUSINESS (BID)
      on delete cascade on update cascade;

alter table REVIEWS
   add constraint FK_REVIEWS_REFERENCE_USERS foreign key (UID)
      references USERS (UID)
      on delete cascade on update cascade;

alter table REVIEWS
   add constraint FK_REVIEWS_REFERENCE_BUSINESS foreign key (BID)
      references BUSINESS (BID)
      on delete cascade on update cascade;

alter table TIPS
   add constraint FK_TIPS_REFERENCE_BUSINESS foreign key (BID)
      references BUSINESS (BID)
      on delete cascade on update cascade;

alter table TIPS
   add constraint FK_TIPS_REFERENCE_USERS foreign key (UID)
      references USERS (UID)
      on delete cascade on update cascade;

alter table WEATHER
   add constraint FK_WEATHER_REFERENCE_STATIOND foreign key (SID)
      references STATIONDATA (SID)
      on delete cascade on update cascade;

