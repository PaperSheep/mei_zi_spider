用多线程

用Mongodb存放数据

get_cover_and_album_main()  # 先运行这个,然后注释掉
                            # 主要把整站的相册和封面链接存在Mongodb里
                            
get_pic_url_main()  # 然后运行这行, 运行结束后注释掉这行
                    # 主要把整站的图片链接存在Mongodb里
                    
download_pic_main()  # 最后运行这行，爬取整站图片

均采用多线程
             
