VERSION=`git rev-parse --short HEAD`
TOKEN="YOUR-GITHUB-TOKEN-HERE"

rm -rf build
npm run build
cp -rf xajax build 
cp -rf sounds build/ 

tar czvf out.tgz build

curl -i -s -k -X POST -H "Content-Type: application/json" "https://api.github.com/repos/DigitalHealthSolutions/web-ui/releases?access_token=$TOKEN" -d "{\"tag_name\": \"$VERSION\", \"target_commitish\": \"master\", \"name\": \"$VERSION\", \"body\": \"Release of commit hash $VERSION\", \"draft\": false, \"prerelease\": false}"

ID=`curl -H "Authorization: token $TOKEN" \
	-H "Accept: application/vnd.github.manifold-preview" \
	"https://api.github.com/repos/DigitalHealthSolutions/web-ui/releases/latest" \
  | jq ".id"`

echo "ID is $ID"

curl -H "Authorization: token $TOKEN" \
	-H "Accept: application/vnd.github.manifold-preview" \
	-H "Content-Type: application/x-compressed" \
	--data-binary @out.tgz \
	"https://uploads.github.com/repos/DigitalHealthSolutions/web-ui/releases/$ID/assets?name=web-ui-$VERSION.tgz"

rm out.tgz
