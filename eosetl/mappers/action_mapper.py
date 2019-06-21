# MIT License
#
# Copyright (c) Vasiliy Bondarenko vabondarenko@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.


class EosActionMapper(object):

    def action_to_dict(self, action, transaction_dict):
        # remember to update
        # blocks_item_exporter.py as well

        result = {
            'type': 'action',
            'transaction_hash': transaction_dict['trx.hash'],
            'block_hash': transaction_dict['block_hash'],
            'account': action['account'],
            'name': action['name'],
            'authorization': action['authorization'],
            'data': action['data'],
            'hex_data': action['hex_data'] if 'hex_data' in action else 'NULL',
        }

        action.pop('account', None)
        action.pop('name', None)
        action.pop('authorization', None)
        action.pop('data', None)
        action.pop('hex_data', None)
        # unset all this fields and check what's left
        if action != {}:
            print('raw action: {}'.format(action))

        return result
