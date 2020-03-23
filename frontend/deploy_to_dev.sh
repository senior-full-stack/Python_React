#!/usr/bin/env bash
rm -rf build
npm run build
cp -R xajax build/xajax
ssh admin@dev.digitalhealths.com "rm -r /tmp/build/*"
scp build/* admin@dev.digitalhealths.com:/tmp/build/
ssh admin@dev.digitalhealths.com "sudo su dm_webapp -c 'rm ~/uixx/*'"
ssh admin@dev.digitalhealths.com "sudo su dm_webapp -c 'cp -R /tmp/build/* ~/uixx/'"
