class Config {
	constructor(){
		this.baseHost = process.env.BASE_HOST || 'http://192.168.209.51:5666';
		this.baseUrl = process.env.BASE_URL || "";
		this.APIVersion = process.env.API_VERSION || "v1";
	}
}
export default Config;