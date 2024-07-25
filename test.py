import hashlib

# 示例数据，可以替换为实际文件内容或其他数据
data_list = ["43712", "2210910310", "薛俊", "xuejun", "2210910310", "14193", "34132220031203602X", "03602X", "203602", "602X", "tjgd03602X", "Xj@03602X", "Xj@20031203", "22320301810782", "20031203", "15298780447", "2879862438", "6222030302021554637"]

# 尝试不同的哈希函数
hash_functions = {
    "MD5": hashlib.md5,
    # "SHA1": hashlib.sha1,
    # "SHA224": hashlib.sha224,
    # "SHA256": hashlib.sha256,
    # "SHA384": hashlib.sha384,
    # "SHA512": hashlib.sha512
}

target_hash = "f2fd16b1fe5054e8a52d54ac4d41e335"

for data in data_list:
    for name, hash_func in hash_functions.items():
        hash_value = hash_func(data.encode()).hexdigest()
        if hash_value == target_hash:
            print(f"Match found with {name}: {data} -> {hash_value}")
        else:
            print(f"No match with {name}: {data} -> {hash_value}")
