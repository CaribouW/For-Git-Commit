# import os
#
#
# def hash_download(hashcode, source_path, target_path):
#     # dgit facebook/react/src -r b5ac963
#     command = 'dgit {} -r {} {}'.format(source_path, hashcode, target_path)
#     return os.popen(command).read()
#
#
# hash_download('99d742c0b74a4a80330c87b6b870909d2f80345f',
#               'facebook/react-native/ReactAndroid/src/main/java/com/facebook/react/modules/location/PositionError.java',
#               './download/')
