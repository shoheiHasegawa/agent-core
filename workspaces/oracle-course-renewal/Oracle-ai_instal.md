■AWS EC2 Oracle26ai										
										
	１．EC2を構築									
		以下の構成で構築								
		VPC				172.31.0.0/16				
		Subnet				172.31.0.0/20				
		SecurityGroup				Inbound 22を許可				
		EC2								
			AMI			Amazon Linux 2023 kernel-6.1 AMI 64bit x86				
			インスタンスタイプ			t3.small				
			キーペア			251st_oracle.pem				
										
	２．事前設定									
		メモリが少ないのでSwapを作成する。								
		$	sudo su -							
		#	dd if=/dev/zero of=/swapfile bs=128M count=32							
		#	chmod 600 /swapfile							
		#	mkswap /swapfile							
		#	swapon /swapfile							
		#	sh -c 'echo "/swapfile swap swap defaults 0 0" >> /etc/fstab'							
		#	free -h							
			               total        used        free      shared  buff/cache   available							
			Mem:           1.9Gi       169Mi       185Mi       0.0Ki       1.5Gi       1.6Gi							
			Swap:          4.0Gi          0B       4.0Gi							
										
	２．Oracle26aiインストール									
		RPMベースでインストールする。								
		以下でOracleインストールするための基本的な設定を全て賄える。								
		#	wget https://yum.oracle.com/repo/OracleLinux/OL9/appstream/x86_64/getPackage/oracle-database-preinstall-23ai-1.0-3.el9.x86_64.rpm							
		#	dnf install -y libxcrypt-compat libnsl							
			Last metadata expiration check: 0:17:27 ago on Wed Feb 11 07:39:09 2026.							
			Dependencies resolved.							
			================================================================================							
			 Package             Arch      Version                     Repository      Size							
			================================================================================							
			Installing:							
			 libnsl              x86_64    2.34-231.amzn2023.0.3       amazonlinux     67 k							
			 libxcrypt-compat    x86_64    4.4.33-7.amzn2023           amazonlinux     92 k							
										
			Transaction Summary							
			================================================================================							
			Install  2 Packages							
										
			Total download size: 159 k							
			Installed size: 297 k							
			Downloading Packages:							
			(1/2): libxcrypt-compat-4.4.33-7.amzn2023.x86_6 2.0 MB/s |  92 kB     00:00    							
			(2/2): libnsl-2.34-231.amzn2023.0.3.x86_64.rpm  1.2 MB/s |  67 kB     00:00    							
			--------------------------------------------------------------------------------							
			Total                                           1.6 MB/s | 159 kB     00:00     							
			Running transaction check							
			Transaction check succeeded.							
			Running transaction test							
			Transaction test succeeded.							
			Running transaction							
			  Preparing        :                                                        1/1 							
			  Installing       : libxcrypt-compat-4.4.33-7.amzn2023.x86_64              1/2 							
			  Installing       : libnsl-2.34-231.amzn2023.0.3.x86_64                    2/2 							
			  Running scriptlet: libnsl-2.34-231.amzn2023.0.3.x86_64                    2/2 							
			  Verifying        : libnsl-2.34-231.amzn2023.0.3.x86_64                    1/2 							
			  Verifying        : libxcrypt-compat-4.4.33-7.amzn2023.x86_64              2/2 							
										
			Installed:							
			  libnsl-2.34-231.amzn2023.0.3.x86_64 libxcrypt-compat-4.4.33-7.amzn2023.x86_64							
										
			Complete!							
										
		#	rpm -ivh --nodeps oracle-database-preinstall-23ai-1.0-3.el9.x86_64.rpm 							
			warning: oracle-database-preinstall-23ai-1.0-3.el9.x86_64.rpm: Header V3 RSA/SHA256 Signature, key ID 8d8b756f: NOKEY							
			Verifying...                          ################################# [100%]							
			Preparing...                          ################################# [100%]							
			Updating / installing...							
			   1:oracle-database-preinstall-23ai-1################################# [100%]							
										
		#	ln -s /etc/system-release /etc/redhat-release							
										
		以下でインターネットからOracle26aiのインストーラをダウンロード								
		#	wget https://download.oracle.com/otn-pub/otn_software/db-free/oracle-ai-database-free-26ai-23.26.0-1.el8.x86_64.rpm							
										
		Oracle26aiインストール								
		#	rpm -ivh --nodeps oracle-ai-database-free-26ai-23.26.0-1.el8.x86_64.rpm 							
			warning: oracle-ai-database-free-26ai-23.26.0-1.el8.x86_64.rpm: Header V3 RSA/SHA256 Signature, key ID ad986da3: NOKEY							
			Verifying...                          ################################# [100%]							
			Preparing...                          ################################# [100%]							
			Updating / installing...							
			   1:oracle-ai-database-free-26ai-23.2################################# [100%]							
			[INFO] Executing post installation scripts...							
			[INFO] Oracle home installed successfully and ready to be configured.							
			To configure Oracle AI Database Free, optionally modify the parameters in '/etc/sysconfig/oracle-free-26ai.conf' and then run '/etc/init.d/oracle-free-26ai configure' as root.							
										
		#	ls -ld /opt/oracle/product/26ai/dbhomeFree							
			drwxrwxr-x. 63 oracle oinstall 16384 Feb 11 08:10 /opt/oracle/product/26ai/dbhomeFree							
										
	３．Oracle Databaseの作成と構成									
		以下の構成で作成。								
			・プラガブルデータベース(FREEPDB1)１つを持つコンテナデータベース(FREE)を作成							
			・デフォルトのポート1521でリスナーを構成							
										
		#	/etc/init.d/oracle-free-26ai configure							
			Specify a password to be used for database accounts. Oracle recommends that the password entered should be at least 8 characters in length, contain at least 1 uppercase character, 1 lower case character and 1 digit [0-9]. Note that the same password will be used for SYS, SYSTEM and PDBADMIN accounts:							
			Confirm the password:							
			Configuring Oracle Listener.							
			Listener configuration succeeded.							
			Configuring Oracle AI Database FREE.							
			Enter SYS user password: 							
			********							
			Enter SYSTEM user password: 							
			*******							
			Enter PDBADMIN User Password: 							
			*******							
			Prepare for db operation							
			7% complete							
			Copying database files							
			29% complete							
			Creating and starting Oracle instance							
			30% complete							
			33% complete							
			36% complete							
			39% complete							
			43% complete							
			Completing Database Creation							
			47% complete							
			49% complete							
			50% complete							
			Creating Pluggable Databases							
			54% complete							
			71% complete							
			Executing Post Configuration Actions							
			93% complete							
			Running Custom Scripts							
			100% complete							
			Database creation complete. For details check the logfiles at:							
			 /opt/oracle/cfgtoollogs/dbca/FREE.							
			Database Information:							
			Global Database Name:FREE							
			System Identifier(SID):FREE							
			Look at the log file "/opt/oracle/cfgtoollogs/dbca/FREE/FREE.log" for further details.							
										
			Connect to Oracle AI Database using one of the connect strings:							
			     Pluggable database: ip-172-31-14-201.ap-northeast-1.compute.internal/FREEPDB1							
			     Multitenant container database: ip-172-31-14-201.ap-northeast-1.compute.internal							
										
		oracleユーザにスイッチ								
		#	su - oracle							
										
		環境変数の設定								
		$	export ORACLE_SID=FREE							
		$	export ORAENV_ASK=NO							
		$	export NLS_LANG=Japanese_Japan.AL32UTF8							
		$	. /opt/oracle/product/26ai/dbhomeFree/bin/oraenv							
			The Oracle base has been set to /opt/oracle							
										
		Oracle Database 26ai に接続								
		$	sqlplus sys@localhost:1521/freepdb1 as sysdba							
										
			SQL*Plus: Release 23.26.0.0.0 - Production on 水 2月 11 08:23:04 2026							
			Version 23.26.0.0.0							
										
			Copyright (c) 1982, 2025, Oracle.  All rights reserved.							
										
			パスワードを入力してください: 							
										
										
			Oracle AI Database 26ai Free Release 23.26.0.0.0 - Develop, Learn, and Run for Free							
			Version 23.26.0.0.0							
			に接続されました。							
										
		表領域の作成								
		SQL>		Create bigfile tablespace tbs2						
				Datafile 'bigtbs_f2.dbf' SIZE 1G AUTOEXTEND						
				ON next 32m maxsize unlimited extent management local segment space management auto;						
										
			表領域が作成されました。							
										
		UNDO表領域の作成								
		SQL>		CREATE UNDO TABLESPACE undots2 						
				DATAFILE 'undotbs_2a.dbf' SIZE 1G AUTOEXTEND ON RETENTION GUARANTEE;						
										
			表領域が作成されました。							
										
		一時表領域の作成								
		SQL>		CREATE TEMPORARY TABLESPACE temp02						
				TEMPFILE 'temp02.dbf' SIZE 100M AUTOEXTEND ON;						
										
			表領域が作成されました。							
										
		boldユーザ作成								
		SQL>		CREATE USER bold						
				IDENTIFIED BY bold						
				DEFAULT TABLESPACE tbs2 QUOTA UNLIMITED ON tbs2;						
										
			ユーザーが作成されました。							
										
		権限の追加（DBA）								
		SQL>		GRANT DBA TO bold;						
										
		SQL Plusから抜ける								
		SQL>		quit						
										
		環境変数の永続化								
		$	vi ~/.bash_profile							
			★最終行に以下を追記							
			export ORACLE_SID=FREE							
			export ORAENV_ASK=NO							
			export NLS_LANG=Japanese_Japan.AL32UTF8							
			export PATH=$PATH:/opt/oracle/product/26ai/dbhomeFree/bin							
			export ORACLE_BASE=/opt/oracle							
			export ORACLE_HOME=/opt/oracle/product/26ai/dbhomeFree							
										
		$	exit							
										
	４．Oracle自動起動設定									
		systemd登録								
		#	vi /etc/systemd/system/oracle-26ai.service							
			★以下内容を貼り付ける							
			[Unit]							
			Description=Oracle Database 26ai Service							
			After=network.target							
										
			[Service]							
			Type=forking							
			User=oracle							
			Environment=ORACLE_HOME=/opt/oracle/product/26ai/dbhomeFree							
			Environment=ORACLE_SID=FREE							
			ExecStart=/opt/oracle/product/26ai/dbhomeFree/bin/dbstart $ORACLE_HOME							
			ExecStop=/opt/oracle/product/26ai/dbhomeFree/bin/dbshut $ORACLE_HOME							
			Restart=on-failure							
										
			[Install]							
			WantedBy=multi-user.target							
										
		サービスの有効化								
		#	systemctl daemon-reload							
		#	systemctl enable oracle-26ai.service							
			Created symlink /etc/systemd/system/multi-user.target.wants/oracle-26ai.service → /etc/systemd/system/oracle-26ai.service.							
										
		oratabの編集								
		#	vi /etc/oratab							
			★以下を編集							
			FREE:/opt/oracle/product/26ai/dbhomeFree:N							
				↓						
			FREE:/opt/oracle/product/26ai/dbhomeFree:Y							
										
	５．Oracle操作									
	５−１．PDB自動起動設定									
		#	su - oracle							
		$	sqlplus / as sysdba							
		SQL>		show pdbs						
			    CON_ID CON_NAME			  OPEN MODE  RESTRICTED				
			---------- ------------------------------ ---------- ----------							
				 2 PDB$SEED			  READ ONLY  NO			
				 3 FREEPDB1			  MOUNTED			
										
		SQL>		alter session set container=freepdb1;						
										
			セッションが変更されました。							
										
		SQL>		alter database open;						
										
			データベースが変更されました。							
										
		SQL>		alter pluggable database freepdb1 save state;						
										
			プラガブル・データベースが変更されました。							
										
	５−２．ローカルネーミングメソッドの設定									
		$	vi $ORACLE_HOME/network/admin/tnsnames.ora							
			★以下の赤枠をコピーして編集							
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
			↓コピー							
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
										
		PDBにローカルネーミングメソッドでログイン								
		$	sqlplus system/oracle@freepdb1							
		SQL>		show con_name;						
			CON_NAME							
			------------------------------							
			FREEPDB1							
										
	５−２．表領域作成、拡張、削除									
		作成								
		SQL>		CREATE TABLESPACE test_tbs						
				DATAFILE 'test_tbs.dbf'						
				SIZE 10M AUTOEXTEND OFF;						
		拡張								
		SQL>		ALTER DATABASE						
				DATAFILE 'test_tbs.dbf'						
				RESIZE 20M;						
		削除								
		SQL>		DROP TABLESPACE test_tbs						
				INCLUDING CONTENTS AND DATAFILES;						
										
	５−３．アーカイブログモード変更									
		$	sqlplus / as sysdba							
		SQL>		archive log list						
			データベース・ログ・モード     非アーカイブ・モード							
			自動アーカイブ                 使用禁止							
			アーカイブ先                    /opt/oracle/product/26ai/dbhomeFree/dbs/arch							
			最も古いオンライン・ログ順序   2							
			現行のログ順序               1							
		SQL>		shutdown immediate						
			データベースがクローズされました。							
			データベースがディスマウントされました。							
			ORACLEインスタンスがシャットダウンされました。							
		SQL>		startup mount						
			ORACLEインスタンスが起動しました。							
										
			Total System Global Area  600601064 bytes							
			Fixed Size		    5009896 bytes					
			Variable Size		  310378496 bytes					
			Database Buffers	  281018368 bytes						
			Redo Buffers		    4194304 bytes					
			データベースがマウントされました。							
		SQL>		alter database archivelog;						
										
			データベースが変更されました。							
										
		SQL>		alter database open;						
										
			データベースが変更されました。							
										
		SQL>		archive log list						
			データベース・ログ・モード     アーカイブ・モード							
			自動アーカイブ                 有効							
			アーカイブ先                    /opt/oracle/product/26ai/dbhomeFree/dbs/arch							
			最も古いオンライン・ログ順序   2							
			アーカイブする次のログ順序    2							
			現行のログ順序               1							
										
	５−４．データベースバックアップ									
		SQL>		exit						
		$	rman target /							
		RMAN>		backup database;						
			backup database;							
			backupを26-02-11で開始しています							
			リカバリ・カタログのかわりにターゲット・データベース制御ファイルを使用しています							
			チャネル: ORA_DISK_1が割り当てられました							
			チャネルORA_DISK_1: SID=49 デバイス・タイプ=DISK							
			チャネルORA_DISK_1: フル・データファイル・バックアップ・セットを開始しています							
			チャネルORA_DISK_1: バックアップ・セットにデータファイルを指定しています							
			入力データファイル ファイル番号=00016 名前=/opt/oracle/product/26ai/dbhomeFree/dbs/bigtbs_f2.dbf							
			入力データファイル ファイル番号=00017 名前=/opt/oracle/product/26ai/dbhomeFree/dbs/undotbs_2a.dbf							
			入力データファイル ファイル番号=00013 名前=/opt/oracle/oradata/FREE/FREEPDB1/sysaux01.dbf							
			入力データファイル ファイル番号=00012 名前=/opt/oracle/oradata/FREE/FREEPDB1/system01.dbf							
			入力データファイル ファイル番号=00014 名前=/opt/oracle/oradata/FREE/FREEPDB1/undotbs01.dbf							
			入力データファイル ファイル番号=00015 名前=/opt/oracle/oradata/FREE/FREEPDB1/users01.dbf							
			チャネルORA_DISK_1: ピース1 (26-02-11)を起動します							
			チャネルORA_DISK_1: ピース1 (26-02-11)が完了しました							
			ピース・ハンドル=/opt/oracle/product/26ai/dbhomeFree/dbs/01nmfmen_1_1_1 タグ=TAG20260211T083326 コメント=NONE							
			チャネルORA_DISK_1: バックアップ・セットが完了しました。経過時間: 00:00:15							
			チャネルORA_DISK_1: フル・データファイル・バックアップ・セットを開始しています							
			チャネルORA_DISK_1: バックアップ・セットにデータファイルを指定しています							
			入力データファイル ファイル番号=00001 名前=/opt/oracle/oradata/FREE/system01.dbf							
			入力データファイル ファイル番号=00003 名前=/opt/oracle/oradata/FREE/sysaux01.dbf							
			入力データファイル ファイル番号=00011 名前=/opt/oracle/oradata/FREE/undotbs01.dbf							
			入力データファイル ファイル番号=00007 名前=/opt/oracle/oradata/FREE/users01.dbf							
			チャネルORA_DISK_1: ピース1 (26-02-11)を起動します							
			チャネルORA_DISK_1: ピース1 (26-02-11)が完了しました							
			ピース・ハンドル=/opt/oracle/product/26ai/dbhomeFree/dbs/026nfmf6_2_1_1 タグ=TAG20260211T083326 コメント=NONE							
			チャネルORA_DISK_1: バックアップ・セットが完了しました。経過時間: 00:00:25							
			チャネルORA_DISK_1: フル・データファイル・バックアップ・セットを開始しています							
			チャネルORA_DISK_1: バックアップ・セットにデータファイルを指定しています							
			入力データファイル ファイル番号=00004 名前=/opt/oracle/oradata/FREE/pdbseed/sysaux01.dbf							
			入力データファイル ファイル番号=00002 名前=/opt/oracle/oradata/FREE/pdbseed/system01.dbf							
			入力データファイル ファイル番号=00009 名前=/opt/oracle/oradata/FREE/pdbseed/undotbs01.dbf							
			チャネルORA_DISK_1: ピース1 (26-02-11)を起動します							
			チャネルORA_DISK_1: ピース1 (26-02-11)が完了しました							
			ピース・ハンドル=/opt/oracle/product/26ai/dbhomeFree/dbs/03vnfmfv_3_1_1 タグ=TAG20260211T083326 コメント=NONE							
			チャネルORA_DISK_1: バックアップ・セットが完了しました。経過時間: 00:00:15							
			backupを26-02-11で終了しました							
										
			Control File and SPFILE Autobackupを26-02-11で開始しています							
			ピース・ハンドル=/opt/oracle/product/26ai/dbhomeFree/dbs/c-1496979115-20260211-00 コメント=NONE							
			Control File and SPFILE Autobackupを26-02-11で終了しました							
										
	５−５．データベースリカバリ									
		RMAN>		shutdown;						
			shutdown;							
			データベースがクローズしました							
			データベースがディスマウントされました。							
			Oracleインスタンスがシャットダウンしました							
										
		RMAN>		startup mount;						
			startup mount;							
			ターゲット・データベースに接続しました(起動していません)。							
			Oracleインスタンスが起動しました							
			データベースがマウントされました。							
										
			システム・グローバル領域の合計は、    600601064バイトです。							
										
			Fixed Size                     5009896バイト							
			Variable Size                318767104バイト							
			Database Buffers             272629760バイト							
			Redo Buffers                   4194304バイト							
										
										
		RMAN>		restore database;						
			restore database;							
			restoreを26-02-11で開始しています							
			チャネル: ORA_DISK_1が割り当てられました							
			チャネルORA_DISK_1: SID=33 デバイス・タイプ=DISK							
										
			データファイル2をスキップしています。すでにファイル/opt/oracle/oradata/FREE/pdbseed/system01.dbfにリストアされています							
			データファイル4をスキップしています。すでにファイル/opt/oracle/oradata/FREE/pdbseed/sysaux01.dbfにリストアされています							
			データファイル9をスキップしています。すでにファイル/opt/oracle/oradata/FREE/pdbseed/undotbs01.dbfにリストアされています							
			チャネルORA_DISK_1: データファイル・バックアップ・セットのリストアを開始しています							
			チャネルORA_DISK_1: バックアップ・セットからリストアするデータファイルを指定しています							
			チャネルORA_DISK_1: データファイル00012を/opt/oracle/oradata/FREE/FREEPDB1/system01.dbfにリストアしています							
			チャネルORA_DISK_1: データファイル00013を/opt/oracle/oradata/FREE/FREEPDB1/sysaux01.dbfにリストアしています							
			チャネルORA_DISK_1: データファイル00014を/opt/oracle/oradata/FREE/FREEPDB1/undotbs01.dbfにリストアしています							
			チャネルORA_DISK_1: データファイル00015を/opt/oracle/oradata/FREE/FREEPDB1/users01.dbfにリストアしています							
			チャネルORA_DISK_1: データファイル00016を/opt/oracle/product/26ai/dbhomeFree/dbs/bigtbs_f2.dbfにリストアしています							
			チャネルORA_DISK_1: データファイル00017を/opt/oracle/product/26ai/dbhomeFree/dbs/undotbs_2a.dbfにリストアしています							
			チャネルORA_DISK_1: バックアップ・ピース/opt/oracle/product/26ai/dbhomeFree/dbs/01nmfmen_1_1_1から読取り中です							
			チャネルORA_DISK_1: ピース・ハンドル=/opt/oracle/product/26ai/dbhomeFree/dbs/01nmfmen_1_1_1 タグ=TAG20260211T083326							
			チャネルORA_DISK_1: バックアップ・ピース1がリストアされました							
			チャネルORA_DISK_1: リストアが完了しました。経過時間: 00:00:35							
			チャネルORA_DISK_1: データファイル・バックアップ・セットのリストアを開始しています							
			チャネルORA_DISK_1: バックアップ・セットからリストアするデータファイルを指定しています							
			チャネルORA_DISK_1: データファイル00001を/opt/oracle/oradata/FREE/system01.dbfにリストアしています							
			チャネルORA_DISK_1: データファイル00003を/opt/oracle/oradata/FREE/sysaux01.dbfにリストアしています							
			チャネルORA_DISK_1: データファイル00007を/opt/oracle/oradata/FREE/users01.dbfにリストアしています							
			チャネルORA_DISK_1: データファイル00011を/opt/oracle/oradata/FREE/undotbs01.dbfにリストアしています							
			チャネルORA_DISK_1: バックアップ・ピース/opt/oracle/product/26ai/dbhomeFree/dbs/026nfmf6_2_1_1から読取り中です							
			チャネルORA_DISK_1: ピース・ハンドル=/opt/oracle/product/26ai/dbhomeFree/dbs/026nfmf6_2_1_1 タグ=TAG20260211T083326							
			チャネルORA_DISK_1: バックアップ・ピース1がリストアされました							
			チャネルORA_DISK_1: リストアが完了しました。経過時間: 00:00:25							
			restoreを26-02-11で終了しました							
										
										
		RMAN>		recover database;						
			recover database;							
			recoverを26-02-11で開始しています							
			チャネルORA_DISK_1の使用							
										
			メディア・リカバリを開始しています							
			メディア・リカバリが完了しました。経過時間: 00:00:00							
										
			recoverを26-02-11で終了しました							
										
										
		RMAN>		alter database open;						
			alter database open;							
			文が処理されました							
										