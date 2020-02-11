import json

import numpy as np
from keras import Model, Input
from keras.engine.saving import load_model
hidden_dim = 64  # 隐藏层的unit个数
epoches = 200
batch_size = 32

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

model = load_model('time-model.h5')


encoder_inputs = model.input[0]  # input_1
encoder_outputs, state_h_enc, state_c_enc = model.layers[2].output  # lstm_1
encoder_states = [state_h_enc, state_c_enc]
encoder_model = Model(encoder_inputs, encoder_states)

decoder_inputs = model.input[1]  # input_2
decoder_state_input_h = Input(shape=(hidden_dim,), name='input_3')
decoder_state_input_c = Input(shape=(hidden_dim,), name='input_4')
decoder_states_inputs = [decoder_state_input_h, decoder_state_input_c]
decoder_lstm = model.layers[3]
decoder_outputs, state_h_dec, state_c_dec = decoder_lstm(
    decoder_inputs, initial_state=decoder_states_inputs)
decoder_states = [state_h_dec, state_c_dec]
decoder_dense = model.layers[4]
decoder_outputs = decoder_dense(decoder_outputs)
decoder_model = Model(
    [decoder_inputs] + decoder_states_inputs,
    [decoder_outputs] + decoder_states)

# Reverse-lookup token index to decode sequences back to
# something readable.
reverse_input_char_index = dict(
    (i, char) for char, i in input_token_index.items())
reverse_target_char_index = dict(
    (i, char) for char, i in target_token_index.items())


# Decodes an input sequence.  Future work should support beam search.
def decode_sequence(input_seq):
    # Encode the input as state vectors.
    states_value = encoder_model.predict(input_seq)

    # Generate empty target sequence of length 1.
    target_seq = np.zeros((1, 1, T_y))
    # Populate the first character of target sequence with the start character.
    target_seq[0, 0, 0] = 1.

    # Sampling loop for a batch of sequences
    # (to simplify, here we assume a batch of size 1).
    stop_condition = False
    decoded_sentence = ''
    while not stop_condition:
        output_tokens, h, c = decoder_model.predict(
            [target_seq] + states_value)

        # Sample a token
        sampled_token_index = np.argmax(output_tokens[0, -1, :])
        sampled_char = reverse_target_char_index[sampled_token_index]
        decoded_sentence += sampled_char

        # Exit condition: either hit max length
        # or find stop character.
        if (sampled_char == '\n' or
                len(decoded_sentence) > max_target_size):
            stop_condition = True

        # Update the target sequence (of length 1).
        target_seq = np.zeros((1, 1, T_y))
        target_seq[0, 0, sampled_token_index] = 1.

        # Update states
        states_value = [h, c]

    return decoded_sentence

rate = int(0.8 * len(encode_input))
X_train_encode = encode_input[:rate]
X_train_decode = decode_input[:rate]
y_train = decode_target[:rate]
# for test
X_test_encode = encode_input[rate:]
X_test_decode = decode_input[rate:]
y_test = decode_target[rate:]

for seq_index in range(100):
    # Take one sequence (part of the training set)
    # for trying out decoding.
    input_seq = encode_input[seq_index: seq_index + 1]
    decoded_sentence = decode_sequence(input_seq)
    print('-')
    print('Input sentence:', input_texts[seq_index])
    print('Decoded sentence:', decoded_sentence[:-2])

