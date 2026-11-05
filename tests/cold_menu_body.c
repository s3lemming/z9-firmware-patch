

static void render(void){mark2_outer_type_text((const char *)(uintptr_t)0x4200b5e2,0,0x46);}
static void audio_request(void){m2_restore_for_audio();}
static void setup(void){
 present[0]=directory[0]=1;present[1]=directory[1]=0;file_missing=0;type_value=0;short_bytes=192;
 root_error=folder_error=collision=mkdir_fail=profile_write_fail=0;extra_files=0;writes=scans=makes=0;
 memset(records,0,sizeof records);memset(record_exists,0,sizeof record_exists);
 T(!m2_profile_encode(records[0][0],10,1,"A:\\CUSTOM_SOUND\\A.WAV"));record_exists[0][0]=1;reset();
 text_calls=refresh_calls=highlight_calls=focus_id=cleared_types=last_mark=0;
}
int main(void){
 setup();mark2_sound_page_refresh((void *)1);T(m2_custom_selected()&&fake.imports==1&&fake.count==3&&fake.scans==1&&fake.published);
 T(!strcmp(outer_text,"CUS")&&writes==0&&*(uint16_t *)(fixture_holder+0x20)==9);uint8_t *owned=fake.last_PCM;unsigned allocated=allocs;
 puts("FIX_1 first_parent_entry_restores_PCM_lists_files_renders_CUS_without_CFG_write PASS");
 for(unsigned i=0;i<5;i++){mark2_sound_page_refresh((void *)1);}
 T(fake.imports==1&&fake.scans==1&&fake.last_PCM==owned&&allocs==allocated&&!strcmp(outer_text,"CUS"));
 puts("FIX_2 repeated_parent_entry_has_no_reimport_rescan_or_extra_allocation PASS");
 mark2_sound_refresh((void *)1);T(highlight_calls==6&&fake.count==3&&fake.imports==1&&cleared_types==31&&focus_id==0x7e21&&last_mark==0x7e21&&!fake.focus_pending);
 puts("FIX_3 child_entry_highlights_reconstructed_current_file PASS");
 setup();mark2_sound_refresh((void *)1);T(m2_custom_selected()&&fake.count==3&&highlight_calls==6&&writes==0&&focus_id==0x7e21);
 puts("FIX_4_direct_child_entry_also_restores PASS");
 setup();audio_request();T(m2_custom_selected()&&fake.count==0);mark2_sound_page_refresh((void *)1);T(fake.count==3&&fake.imports==1&&!strcmp(outer_text,"CUS"));
 puts("FIX_5_sound_restored_before_menu_builds_missing_rows_without_rebinding PASS");
 select_row(0);T(!m2_custom_selected());mark2_sound_page_refresh((void *)1);T(!m2_custom_selected()&&outer_text==(const char *)(uintptr_t)0x4200b5e2);
 puts("REGRESSION_6_explicit_native_selection_does_not_reenable_saved_custom PASS");
 setup();T(!m2_profile_encode(records[0][0],10,0,0));mark2_sound_page_refresh((void *)1);T(!m2_custom_selected()&&fake.count==0&&writes==0&&outer_text==(const char *)(uintptr_t)0x4200b5e2);
 puts("REGRESSION_7_disabled_profile_keeps_native_A PASS");
 setup();records[0][0][156]^=1;mark2_sound_page_refresh((void *)1);T(!m2_custom_selected()&&fake.imports==0&&writes==0);
 puts("REGRESSION_8_bad_CRC_not_displayed_as_custom PASS");
 setup();file_missing=1;mark2_sound_page_refresh((void *)1);T(!m2_custom_selected()&&fake.restore_status==5&&fake.imports==0);
 puts("REGRESSION_9_missing_WAV_not_displayed_as_custom PASS");
 setup();present[1]=directory[1]=1;T(!m2_profile_encode(records[1][0],1,1,"B:\\CUSTOM_SOUND\\A.WAV"));record_exists[1][0]=1;mark2_sound_page_refresh((void *)1);T(!m2_custom_selected()&&fake.restore_status==3&&fake.count==0);
 puts("REGRESSION_10_dual_enabled_profiles_keep_ambiguity_rejection PASS");
 setup();present[0]=0;present[1]=directory[1]=1;T(!m2_profile_encode(records[1][0],1,1,"B:\\CUSTOM_SOUND\\A.WAV"));record_exists[1][0]=1;mark2_sound_page_refresh((void *)1);T(m2_custom_selected()&&fake.count==3&&fake.loaded_path[0]=='B');
 puts("FIX_11_card2_only_restores_and_lists_current_file PASS");
 setup();present[0]=0;mark2_sound_page_refresh((void *)1);T(!m2_custom_selected()&&fake.count==0&&writes==0);
 puts("REGRESSION_12_no_card_no_false_CUS PASS");
 setup();render();T(!m2_custom_selected()&&fake.imports==0&&scans==0);
 puts("CONTRACT_13_text_renderer_stays_IO_free PASS");
 setup();fake.active=1;mark2_sound_page_refresh((void *)1);T(!fake.restore_attempted&&scans==0);fake.active=0;mark2_sound_page_refresh((void *)1);T(m2_custom_selected()&&fake.count==3);
 puts("CONTRACT_14_busy_picker_defers_to_next_entry PASS");


 setup();extra_files=25;T(!m2_profile_encode(records[0][0],10,1,"A:\\CUSTOM_SOUND\\EXTRA24.WAV"));mark2_sound_page_refresh((void *)1);
 T(m2_custom_selected()&&fake.count==20&&fake.overflow==1);char path[128];file_path(path,&fake.files[19]);T(!strcmp(path,fake.loaded_path));
 mark2_sound_refresh((void *)1);T(focus_id==0x7e34&&last_mark==0x7e34&&cleared_types==31&&!fake.focus_pending);
 puts("FIX_16_selected_file_beyond_first20_replaces_last_visible_row_with_same_bound PASS");
 focus_id=0;mark2_sound_refresh((void *)1);T(focus_id==0&&last_mark==0x7e34);
 puts("CONTRACT_17_retained_entry_focus_is_not_reset_after_model_focus_consumed PASS");
 printf("COLD_MENU_PASS cases=16 assertions=%u picker_bytes=%zu\n",cases,sizeof fake);return 0;
}
