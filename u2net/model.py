import tensorflow as tf
from models.import_module import Model_U2Net,Model_UNet3plus

my_model = Model_U2Net(256,3)

# model_path = r'/home/skymap/big_data/Dao_work_space/MRSAC/code/weights/aDao/u2net_256_road_mrsac_v3_lan2_model.h5'
my_model.load_weights(r'/home/skymap/big_data/Dao_work_space/MRSAC/Bang_diem/weights/u2net_256_transcript_mrsac_v1.h5')
my_model.save(r'/home/skymap/big_data/Dao_work_space/MRSAC/Bang_diem/weights/u2net_256_transcript_mrsac_v1_model.h5')
# print(my_model.summary())

# model_farm = tf.keras.models.load_model(model_path)
# print(model_farm.summary())

# 20220826_065957_ssc3_u0001_visual
# 20220821_070453_ssc12_u0001_visual
# 20220820_103902_ssc6_u0001_visual
# 20220813_070157_ssc12_u0002_visual

# sua
# 20220821_070453_ssc12_u0002_visual
# 20220819_102529_ssc8_u0002_visual
# 20220818_073620_ssc1_u0002_visual
# 20220814_103841_ssc10_u0002_visual
# 20220814_103841_ssc10_u0001_visual
# 20220807_064607_ssc4_u0002_visual
# 20220812_070039_ssc4_u0002_visual
# 20220813_070157_ssc12_u0001_visual

