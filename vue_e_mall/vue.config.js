module.exports = {
    publicPath: '',
    devServer:{
        host:'localhost',
        port:8080,
        proxy:{
            '/mock':{
                target:'http://lcoalhost:8080',
                //webpack
                ws:false,
                //将主机头的原点改为目标的url
                changeOrign:false
            }
        }
    }
}