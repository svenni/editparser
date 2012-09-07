import unittest

from editparser import TimeCode

class Test_Timecode_creation(unittest.TestCase):
    def test_defaults(self):
        tc = TimeCode()
        self.assertEquals(tc._base, 24)
        self.assertEquals(tc._frames, 0)
    
    def test_base(self):
        tc = TimeCode(base=30)
        self.assertEquals(tc._base, 30)
        self.assertEquals(tc._frames, 0)

    def test_frames(self):
        tc = TimeCode(frames=20)
        self.assertEquals(tc._base, 24)
        self.assertEquals(tc._frames, 20)

    def test_tc(self):
        tc = TimeCode(tc='00:00:01:00')
        self.assertEquals(tc._base, 24)
        self.assertEquals(tc._frames, 24)

    def test_frames_tc_non_empty(self):
        tc = TimeCode(tc='00:00:01:00', frames=2)
        self.assertEquals(tc._base, 24)
        self.assertEquals(tc._frames, 2)

    def test_frames_tc_tc_empty(self):
        tc = TimeCode(tc='00:00:00:00', frames=2)
        self.assertEquals(tc._base, 24)
        self.assertEquals(tc._frames, 2)

    def test_frames_tc_frames_empty(self):
        tc = TimeCode(tc='00:00:00:12', frames=0)
        self.assertEquals(tc._base, 24)
        self.assertEquals(tc._frames, 12)

    def test_frames_tc_empty(self):
        tc = TimeCode(tc='00:00:00:00', frames=0)
        self.assertEquals(tc._frames, 0)
        
    
class Test_basic_functions(unittest.TestCase):
    def setUp(self):
        self.tc1 = TimeCode(frames=4)
        self.tc2 = TimeCode(frames=3)
    
    def test_get_frames(self):
        self.assertEquals(self.tc1.frames(), 4)

    def test_addition(self):
        new_tc = self.tc1 + self.tc2
        self.assertEquals(new_tc.frames(), 7)

    def test_subtraction(self):
        new_tc = self.tc1 - self.tc2
        self.assertEquals(new_tc.frames(), 1)


class Test_toFrames(unittest.TestCase):
    def setUp(self):
        self.tc = TimeCode()
        self.tc30 = TimeCode(base=30)
    
    def test_frames(self):
        self.assertEquals(self.tc.toFrames('00:00:00:01'), 1)

    def test_seconds(self):
        self.assertEquals(self.tc.toFrames('00:00:01:00'), 24)

    def test_seconds_30fps(self):
        self.assertEquals(self.tc30.toFrames('00:00:01:00'), 30)

    def test_minutes(self):
        self.assertEquals(self.tc.toFrames('00:01:00:00'), 1440)

    def test_minute_30fps(self):
        self.assertEquals(self.tc30.toFrames('00:01:00:00'), 1800)

    def test_hour(self):
        self.assertEquals(self.tc.toFrames('01:00:00:00'), 86400)

    def test_hour_30fps(self):
        self.assertEquals(self.tc30.toFrames('01:00:00:00'), 108000)

    def test_all_fields(self):
        self.assertEquals(self.tc.toFrames('01:02:03:04'), 89356)

    def test_all_fields_30fps(self):
        self.assertEquals(self.tc30.toFrames('01:02:03:04'), 111694)

    def test_negative_tc(self):
        self.assertEquals(self.tc.toFrames('-00:00:01:02'), -26)

    def test_invalid_codes(self):
        self.assertRaises(RuntimeError, self.tc.toFrames, 'abc')
        self.assertRaises(RuntimeError, self.tc.toFrames, '00:00:00')
        self.assertRaises(RuntimeError, self.tc.toFrames, '00:00')
        self.assertRaises(RuntimeError, self.tc.toFrames, '')
        self.assertRaises(RuntimeError, self.tc.toFrames, '00:00:00:00:00') 
    

if __name__ == '__main__':
    unittest.main()
