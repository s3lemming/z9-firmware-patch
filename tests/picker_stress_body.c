/* Included after the baseline ABI fixture, whose main is renamed. */
int main(void){
 int rc=baseline_main();assert(!rc);unsigned operations=0;
 /* Direct original-entry consumers: empty/one/20/21, directory attributes,
  * dual-card identical basenames retain distinct mount identities. */
 uint8_t entry[600]={0};memcpy(entry,"A.WAV",6);reset();fake.active=1;
 publish_rows();T(fake.count==0&&*(uint16_t*)(fixture_holder+0x20)==6);
 collect(entry);publish_rows();T(fake.count==1&&*(uint16_t*)(fixture_holder+0x20)==7);
 for(unsigned i=1;i<20;i++)collect(entry);
 publish_rows();T(fake.count==20&&!fake.overflow&&*(uint16_t*)(fixture_holder+0x20)==26);
 collect(entry);T(fake.count==20&&fake.overflow);
 reset();fake.active=1;entry[0x20e]=0x10;collect(entry);T(!fake.count);
 entry[0x20e]=0;collect(entry);fake.active=2;collect(entry);
 T(fake.count==2&&fake.files[0].root=='A'&&fake.files[1].root=='B');
 const char *invalid="/\\:*?\"<>|";
 for(unsigned i=0;invalid[i];i++){
  uint8_t decoded[112];uint32_t length=0;memset(entry,0,sizeof entry);memcpy(entry,"ALIAS.WAV",10);entry[14]=(uint8_t)invalid[i];
  T(!entry_name(entry,decoded,&length));
 }
 for(unsigned epoch=0;epoch<1000;epoch++){
  present[0]=1;present[1]=0;directory[0]=1;file_missing=0;profile_write_fail=0;
  memset(record_exists,0,sizeof record_exists);reset();short_bytes=192;
  for(unsigned i=0;i<12;i++){select_row(5);operations++;T(fake.count==3&&!fake.attempts);}
  for(unsigned i=0;i<4;i++){select_row(6);operations++;T(selected&&fake.attempts==i+1&&fake.imports==i+1);}
  uint8_t *prior=fake.last_PCM;unsigned prior_writes=writes;
  for(unsigned i=0;i<6;i++){select_row(6);operations++;T(fake.import_status==M2_LIMIT&&fake.attempts==4&&fake.last_PCM==prior&&writes==prior_writes);}
  select_row(0);operations++;T(!selected);m2_restore_for_audio();T(!selected);
  reset();m2_restore_for_audio();operations++;T(!selected&&fake.restore_status==2);
 }
 uint32_t seed=0x319531u;
 for(unsigned trial=0;trial<10000;trial++){
  uint8_t ent[600]={0},decoded[112];uint32_t n=0;
  seed=1664525u*seed+1013904223u;unsigned len=seed%114u;
  memcpy(ent,"ALIAS.WAV",10);
  for(unsigned i=0;i<len;i++)ent[14+2*i]='x';
  int valid=entry_name(ent,decoded,&n);
  T(valid==(len==0||len<=111));if(len&&len<=111)T(n==len);
  operations++;
 }
 printf("MARK2_PICKER_STRESS_PASS operations=%u lifecycle_epochs=1000 filename_seed=0x319531 assertions=%u\n",operations,cases);return 0;
}
