# Imports
import json

import keras.optimizers as opt
import numpy as np
from keras import Model
from keras.layers import Input, LSTM, Dense

hidden_dim = 64  # 隐藏层的unit个数
epoches = 200
batch_size = 32


def tokenize(sentence: 'str', token_map, length):
    ans = np.zeros(shape=(length, len(token_map)), dtype='float32')
    for i, token in enumerate(sentence):
        if token in token_map:
            ans[i][token_map[token]] = 1
    ans[i][0] = 1
    return ans


if __name__ == '__main__':
    with open('dataset/Time Dataset.json', 'r') as f:
        data = json.loads(f.read())

    input_texts, target_texts = [x[0] for x in data], [x[1] for x in data]
    input_vocab, target_vocab = set(), set()
    max_input_size, max_target_size = 0, 0  # 输入序列的最大长度,输出序列的最大长度
    for i, txt in enumerate(data):
        max_input_size = max(max_input_size, len(input_texts[i]))
        max_target_size = max(max_target_size, len(target_texts[i]))
        for token in input_texts[i]:
            if token not in input_vocab:
                input_vocab.add(token)
        for token in target_texts[i]:
            if token not in target_vocab:
                target_vocab.add(token)
    T_x, T_y = len(input_vocab), len(target_vocab)  # 输入序列的token尺寸, 输出序列的token尺寸
    input_vocab = list(input_vocab)
    target_vocab = list(target_vocab)
    input_vocab.sort()
    target_vocab.sort()
    print('input text has max len of {} , and the token number of {}'.format(max_input_size, len(input_vocab)))
    print('target text has max len of {} , and the token number of {}'.format(max_target_size, len(target_vocab)))
    # 进行tokenize
    input_token_index = {}
    target_token_index = {}
    for i, vocab in enumerate(input_vocab):
        input_token_index[vocab] = i
    for i, vocab in enumerate(target_vocab):
        target_token_index[vocab] = i

    # 获取到所有的内容
    encode_input = np.zeros(shape=(
        len(input_texts), max_input_size, T_x
    ))
    decode_input = np.zeros(shape=(
        len(target_texts), max_target_size, T_y
    ))
    decode_target = np.zeros(shape=(
        len(target_texts), max_target_size, T_y
    ))

    for i, (input_sentence, target_sentence) in enumerate(zip(input_texts, target_texts)):
        for t, char in enumerate(input_sentence):
            encode_input[i, t, input_token_index[char]] = 1
        encode_input[i, t, 0] = 1

        for t, char in enumerate(target_sentence):
            decode_input[i, t, target_token_index[char]] = 1
            if t > 0:
                decode_target[i, t - 1, target_token_index[char]] = 1
        decode_input[i, t + 1:, 0] = 1
        decode_target[i, t:, 0] = 1

    # model=====
    # 输入张量
    Encoder_input = Input(shape=(None, T_x))
    # LSTM层
    Encoder_LSTM = LSTM(units=hidden_dim, return_state=True)
    _, Encoder_h, Encoder_c = Encoder_LSTM(Encoder_input)

    Enconder_context = [Encoder_h, Encoder_c]
    # decoder一端
    Decoder_input = Input(shape=(None, T_y))
    Decoder_LSTM = LSTM(units=hidden_dim, return_state=True, return_sequences=True)

    Decoder_out, _, _ = Decoder_LSTM(Decoder_input, initial_state=Enconder_context)
    Decoder_dense = Dense(T_y, activation='softmax')
    Decoder_out = Decoder_dense(Decoder_out)
    # ============================
    model = Model([Encoder_input, Decoder_input], Decoder_out)
    # Run training
    optim = opt.Adagrad()
    model.compile(optimizer='rmsprop', loss='categorical_crossentropy',
                  metrics=['accuracy'])
    model.summary()
    print(np.shape(encode_input))

    rate = int(0.8 * len(encode_input))
    X_train_encode = encode_input[:rate]
    X_train_decode = decode_input[:rate]
    y_train = decode_target[:rate]
    # for test
    X_test_encode = encode_input[rate:]
    X_test_decode = decode_input[rate:]
    y_test = decode_target[rate:]
    model.fit([encode_input, decode_input], decode_target,
              batch_size=batch_size,
              epochs=epoches,
              validation_split=0.2)

    model.save('time-model.h5')

    ans = model.evaluate([X_test_encode, X_test_decode], y_test, verbose=0)
    print("accuracy is {}".format(ans[-1]))
