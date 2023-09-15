drop table if exists FIP_POPULATION_YEAR;

/*==============================================================*/
/* Table: FIP_POPULATION_YEAR                                   */
/*==============================================================*/
create table FIP_POPULATION_YEAR (
   FCODE                VARCHAR(8)                 not null,
   YEAR                 INT8                 null,
   POPULATION           INT8                 null
);

drop table if exists FIP_POPULATION_RACE;

/*==============================================================*/
/* Table: FIP_POPULATION_RACE                                   */
/*==============================================================*/
create table FIP_POPULATION_RACE (
   FCODE                VARCHAR(8)                 not null,
   RACE                 VARCHAR(20)          null,
   PERCENTAGE           DECIMAL(10,9)        null
);

drop table if exists FIP_POPULATION_AGE;

/*==============================================================*/
/* Table: FIP_POPULATION_AGE                                    */
/*==============================================================*/
create table FIP_POPULATION_AGE (
   FCODE                VARCHAR(8)                 not null,
   AGE_RANGE            VARCHAR(10)          null,
   PERCENTAGE           DECIMAL(10,9)        null
);

drop index if exists COUNTIES_PK;

drop table if exists COUNTIES;

/*==============================================================*/
/* Table: COUNTIES                                              */
/*==============================================================*/
create table COUNTIES (
   FCODE                VARCHAR(8)                 not null,
   STATE                VARCHAR(3)           not null,
   COUNTY               VARCHAR(50)          not null,
   LAND_AREA            DECIMAL(17,10)       null,
   AREA                 DECIMAL(17,10)       null,
   LON                  DECIMAL(13,10)       not null,
   LAT                  DECIMAL(13,10)       not null,
   AVG_INCOME           DECIMAL(8,2)         null,
   constraint PK_COUNTIES primary key (FCODE)
);

drop index if exists COUNTIES_FIP_FK;

drop index if exists FIPZIP_PK;

drop table if exists FIPZIP;


/*==============================================================*/
/* Table: FIPZIP                                                */
/*==============================================================*/
create table FIPZIP (
   PCODE                VARCHAR(8)           not null,
   FCODE                VARCHAR(8)                 not null,
   constraint PK_FIPZIP primary key (PCODE)
);

drop index if exists FACILITIES_FIP_FK;

drop index if exists FACILITIES_LOCATION_PK;

drop table if exists FACILITIES_LOCATION;

/*==============================================================*/
/* Table: FACILITIES_LOCATION                                   */
/*==============================================================*/
create table FACILITIES_LOCATION (
   OBJECTID             INT4                 not null,
   PCODE                VARCHAR(8)           not null,
   FAC_TYPE             INT4                 null,
   FAC_NAME             VARCHAR(70)          null,
   LON                  DECIMAL(13,10)       null,
   LAT                  DECIMAL(13,10)       null,
   DATE_UPDTE           DATE                 null,
   CITY                 CHAR(30)             null,
   STATE                VARCHAR(3)           null,
   constraint PK_FACILITIES_LOCATION primary key (OBJECTID)
);

drop index if exists FACILITIES_ON_LOCATION2_FK;

drop table if exists FACILITIES;

/*==============================================================*/
/* Table: FACILITIES                                            */
/*==============================================================*/
create table FACILITIES (
   OBJECTID             INT4                 not null,
   FERRY_T              INT4                 null,
   FERRY_I              INT4                 null,
   BUS_T                INT4                 null,
   BUS_I                INT4                 null,
   BUS_CODE_S           INT4                 null,
   BUS_SUPP             INT4                 null,
   RAIL_I               INT4                 null,
   RAIL_C               INT4                 null,
   RAIL_H               INT4                 null,
   RAIL_LIGHT           INT4                 null,
   AIR_SERVE            INT4                 null,
   BIKE_SHARE           INT4                 null,
   BIKE_SYS             VARCHAR(60)          null,
   I_SERVICE            INT4                 null,
   T_SERVICE            INT4                 null,
   MODES_SERV           INT4                 null,
   MODE_BUS             BOOL                 null,
   MODE_AIR             BOOL                 null,
   MODE_RAIL            BOOL                 null,
   MODE_FERRY           BOOL                 null,
   MODE_BIKE            BOOL                 null
);

alter table FIP_POPULATION_YEAR
   add constraint FK_FIP_POPU_COUNTIES__COUNTIES_YEAR foreign key (FCODE)
      references COUNTIES (FCODE)
      on delete restrict on update restrict;

alter table FIP_POPULATION_RACE
   add constraint FK_FIP_POPU_COUNTIES__COUNTIES_RACE foreign key (FCODE)
      references COUNTIES (FCODE)
      on delete restrict on update restrict;

alter table FIP_POPULATION_AGE
   add constraint FK_FIP_POPU_COUNTIES__COUNTIES_AGE foreign key (FCODE)
      references COUNTIES (FCODE)
      on delete restrict on update restrict;


/*==============================================================*/
/* Index: COUNTIES_PK                                           */
/*==============================================================*/
create unique index COUNTIES_PK on COUNTIES (
FCODE
);

/*==============================================================*/
/* Index: COUNTIES_FIP_FK                                       */
/*==============================================================*/
create  index COUNTIES_FIP_FK on FIPZIP (
FCODE
);

alter table FIPZIP
   add constraint FK_FIPZIP_COUNTIES__COUNTIES foreign key (FCODE)
      references COUNTIES (FCODE)
      on delete restrict on update restrict;

/*==============================================================*/
/* Index: FACILITIES_LOCATION_PK                                */
/*==============================================================*/
create unique index FACILITIES_LOCATION_PK on FACILITIES_LOCATION (
OBJECTID
);

/*==============================================================*/
/* Index: FACILITIES_FIP_FK                                     */
/*==============================================================*/
create  index FACILITIES_FIP_FK on FACILITIES_LOCATION (
PCODE
);


alter table FACILITIES_LOCATION
   add constraint FK_FACILITI_FACILITIE_FIPZIP foreign key (PCODE)
      references FIPZIP (PCODE)
      on delete restrict on update restrict;

/*==============================================================*/
/* Index: FACILITIES_ON_LOCATION2_FK                            */
/*==============================================================*/
create  index FACILITIES_ON_LOCATION2_FK on FACILITIES (
OBJECTID
);

alter table FACILITIES
   add constraint FK_FACILITI_FACILITIE_FACILITI foreign key (OBJECTID)
      references FACILITIES_LOCATION (OBJECTID)
      on delete restrict on update restrict;



