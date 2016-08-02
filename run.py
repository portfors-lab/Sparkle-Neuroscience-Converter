import sys
import h5py
import os
import copy
import json
import operator
import numpy as np

from PyQt4 import QtCore, QtGui
from main_ui import Ui_MainWindow
from itertools import islice, count


def get_file_name(path):
    edit_path = path.replace('/', '\\')
    split_list = edit_path.split('\\')
    return split_list[-1]


class MainForm(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.filename = ''
        self.directory = ''
        self.h_file = h5py.File

        self.chan_dict = {}

        self.ui.progressBar_data.setMaximum(75)

        QtCore.QObject.connect(self.ui.pushButton_browse_open, QtCore.SIGNAL("clicked()"), self.browse)
        QtCore.QObject.connect(self.ui.pushButton_browse_save, QtCore.SIGNAL("clicked()"), self.browse2)
        QtCore.QObject.connect(self.ui.pushButton_start, QtCore.SIGNAL("clicked()"), self.start)
        QtCore.QObject.connect(self.ui.pushButton_auto_threshold, QtCore.SIGNAL("clicked()"), self.auto_threshold)
        QtCore.QObject.connect(self.ui.comboBox_test_num, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.test_change)
        QtCore.QObject.connect(self.ui.comboBox_threshold, QtCore.SIGNAL("currentIndexChanged(const QString&)"), self.chan_change)
        QtCore.QObject.connect(self.ui.doubleSpinBox_threshold, QtCore.SIGNAL("valueChanged(double)"), self.thresh_change)

    def browse(self):
        self.ui.comboBox_test_num.clear()

        QtGui.QFileDialog(self)
        self.filename = QtGui.QFileDialog.getOpenFileName()
        # Make sure proper separators are being used
        self.filename = self.filename.replace('/', os.sep).replace('\\', os.sep)
        self.ui.lineEdit_file_name.setText(self.filename)

        # If the filename is not blank, attempt to extract test numbers and place them into the combobox
        if self.filename != '':
            if '.hdf5' in self.filename:
                try:
                    self.h_file = h5py.File(unicode(self.filename), 'r')
                except IOError:
                    self.ui.textEdit.append('Error: I/O Error\n')
                    return

                tests = {}
                for key in self.h_file.keys():
                    if 'segment' in key:
                        for test in self.h_file[key].keys():
                            tests[test] = int(test.replace('test_', ''))

                sorted_tests = sorted(tests.items(), key=operator.itemgetter(1))

                temp = []
                for test in sorted_tests:
                    temp.append(test[0])
                self.ui.comboBox_test_num.addItems(temp)
            else:
                self.ui.textEdit.append('Error: Must select a .hdf5 file.\n')
                return
        else:
            self.ui.textEdit.append('Error: Must select a file to open.\n')
            return

        if self.ui.lineEdit_output_directory.text() == '':
            temp = copy.copy(self.filename)
            filename_split = self.filename.split(os.sep)
            output = temp.replace(filename_split[-1], '')

            # Make sure proper separators are being used
            output = output.replace('/', os.sep).replace('\\', os.sep)
            self.ui.lineEdit_output_directory.setText(output)

    def browse2(self):
        QtGui.QFileDialog(self)
        self.directory = QtGui.QFileDialog.getExistingDirectory()
        self.ui.lineEdit_output_directory.setText(self.directory)

    def test_change(self):

        filename = self.filename = self.ui.lineEdit_file_name.text()

        # Validate filename
        if filename != '':
            if '.hdf5' in filename:
                try:
                    h_file = h5py.File(unicode(self.filename), 'r')
                    target_test = self.ui.comboBox_test_num.currentText()
                except IOError:
                    self.ui.textEdit.append('Error: I/O Error\n')
                    return
            else:
                self.ui.textEdit.append('Error: Must select a .hdf5 file.\n')
                return
        else:
            self.ui.textEdit.append('Error: Must select a file to open.\n')
            return

        target_seg = None

        # Find target segment
        for segment in h_file.keys():
            for test in h_file[segment].keys():
                if target_test == test:
                    target_seg = segment
                    target_test = test

        if target_seg is None:
            return

        # Add Comments
        try:
            comment = h_file[target_seg].attrs['comment']
            self.ui.lineEdit_comments.setText(comment)
        except:
            self.ui.lineEdit_comments.clear()
            self.ui.textEdit.append("Error: Can't open attribute (Can't locate attribute: 'comment')\n")

        for key in h_file.keys():
            if 'segment' in key:
                for test in h_file[key].keys():
                    if test == self.ui.comboBox_test_num.currentText():
                        # Build site string
                        if len(h_file[key][test].value.shape) > 3:
                            # no_chan = False
                            # traces = h_file[key][test].value.shape[0]
                            # repetitions = h_file[key][test].value.shape[1]
                            channels = h_file[key][test].value.shape[2]
                            # samples = h_file[key][test].value.shape[3]
                        else:
                            # no_chan = True
                            # traces = h_file[key][test].value.shape[0]
                            # repetitions = h_file[key][test].value.shape[1]
                            channels = 1
                            # samples = h_file[key][test].value.shape[2]

        self.ui.comboBox_threshold.clear()
        for chan in islice(count(1), channels):
            self.ui.comboBox_threshold.addItem('channel_' + str(chan))

        h_file.close()

    def chan_change(self):
        if str(self.ui.comboBox_threshold.currentText()) in self.chan_dict:
            self.ui.doubleSpinBox_threshold.setValue(self.chan_dict[str(self.ui.comboBox_threshold.currentText())])
        else:
            self.ui.doubleSpinBox_threshold.setValue(0)

    def thresh_change(self):
        self.chan_dict[str(self.ui.comboBox_threshold.currentText())] = self.ui.doubleSpinBox_threshold.value()

    def auto_threshold(self):
        threshFraction = 0.7

        filename = self.ui.lineEdit_file_name.text()

        # Validate filename
        if filename != '':
            if '.hdf5' in filename:
                try:
                    h_file = h5py.File(unicode(self.filename), 'r')
                    target_test = self.ui.comboBox_test_num.currentText()
                except IOError:
                    self.ui.textEdit.append('Error: I/O Error\n')
                    return
            else:
                self.ui.textEdit.append('Error: Must select a .hdf5 file.\n')
                return
        else:
            self.ui.textEdit.append('Error: Must select a file to open.\n')
            return

        # Find target segment
        for segment in h_file.keys():
            for test in h_file[segment].keys():
                if target_test == test:
                    target_seg = segment
                    target_test = test

        trace_data = h_file[target_seg][target_test].value

        if len(trace_data.shape) == 4:
            # Compute threshold from average maximum of traces
            max_trace = []
            tchan = int(self.ui.comboBox_threshold.currentText().replace('channel_', ''))
            for n in range(len(trace_data[1, :, tchan - 1, 0])):
                max_trace.append(np.max(np.abs(trace_data[1, n, tchan - 1, :])))
            average_max = np.array(max_trace).mean()
            thresh = threshFraction * average_max

        else:
            # Compute threshold from average maximum of traces
            max_trace = []
            for n in range(len(trace_data[1, :, 0])):
                max_trace.append(np.max(np.abs(trace_data[1, n, :])))
            average_max = np.array(max_trace).mean()
            thresh = threshFraction * average_max

        self.ui.doubleSpinBox_threshold.setValue(thresh)

    def convert(self):
        filename = self.ui.lineEdit_file_name.text()
        if filename != '':
            h_file = h5py.File(unicode(self.filename), 'r')

        # Check for extraction parameters
        if '.hdf5' in filename:
            pass
        else:
            self.ui.textEdit.append('Error: Must select a .hdf5 file.\n')
            return

        meta_progress = 0
        data_progress = 0

        temp_filename = get_file_name(self.ui.lineEdit_file_name.text().replace('.hdf5', ''))
        test_name = self.ui.comboBox_test_num.currentText()
        datafile = self.ui.lineEdit_output_directory.text() + os.path.sep + temp_filename + '_' + test_name + '.stad'

        stam = open(self.ui.lineEdit_output_directory.text() + os.path.sep + temp_filename + '_' + test_name + '.stam', 'w')
        stad = open(self.ui.lineEdit_output_directory.text() + os.path.sep + temp_filename + '_' + test_name + '.stad', 'w')

        stam.write('# Data filepath\n')
        stam.write('datafile=' + datafile + ';\n')
        stam.write('#\n')
        stam.write('# Site metadata\n')

        meta_progress += 5
        self.ui.progressBar_meta.setValue(meta_progress)

        site_count = 0
        trace_count = 0
        category_count = 0

        site_string = ''
        category_string = ''
        trace_string = ''

        for key in h_file.keys():
            if 'segment' in key:
                for test in h_file[key].keys():
                    if test == test_name:
                        # Build site string
                        if len(h_file[key][test].value.shape) > 3:
                            no_chan = False
                            traces = h_file[key][test].value.shape[0]
                            repetitions = h_file[key][test].value.shape[1]
                            channels = h_file[key][test].value.shape[2]
                            samples = h_file[key][test].value.shape[3]
                        else:
                            no_chan = True
                            traces = h_file[key][test].value.shape[0]
                            repetitions = h_file[key][test].value.shape[1]
                            channels = 1
                            samples = h_file[key][test].value.shape[2]

                        # The number of stimuli each trace contains
                        stimuli_count = {}

                        channel_progress = 75 / float(channels)
                        for channel in islice(count(1), channels):
                            self.ui.textEdit.append('Channel: ' + str(channel))
                            # Execute only once to create category metadata
                            if channel == 1:
                                for trace in islice(count(1), traces):
                                    stimuli_types = {}
                                    stimuli = json.loads(h_file[key][test].attrs['stim'])
                                    stimulus = stimuli[trace - 1]
                                    for components in stimulus['components']:
                                        # Build category string
                                        category_count += 1
                                        if trace in stimuli_count:
                                            stimuli_count[trace] += 1
                                        else:
                                            stimuli_count[trace] = 1
                                        comment = h_file[key].attrs['comment']  # Test Comment
                                        if components['stim_type'] == 'Vocalization':
                                            # Get only the filename and then remove the extension
                                            stim = os.path.splitext(components['filename'].split('/')[-1])[0]
                                        else:
                                            if components['stim_type'] in stimuli_types:
                                                stimuli_types[components['stim_type']] += 1
                                            else:
                                                stimuli_types[components['stim_type']] = 1
                                            stim = components['stim_type'] + '_' + str(stimuli_types[components['stim_type']])
                                        category_string += 'category=' + str(category_count) + '; '
                                        category_string += 'label='
                                        category_string += 'trace_' + str(trace) + ' ' + stim
                                        category_string += ';\n'
                                    meta_progress += 15 / float(traces)
                                    self.ui.progressBar_meta.setValue(meta_progress)

                            cat_count = 0
                            trace_progress = channel_progress / float(len(stimuli_count.keys()))
                            for trace in stimuli_count.keys():
                                self.ui.textEdit.append('Channel: ' + str(channel) + '  Trace: ' + str(trace))
                                stimuli = json.loads(h_file[key][test].attrs['stim'])
                                stimulus = stimuli[trace - 1]
                                if stimuli_count[trace] < 2:
                                    for rep in islice(count(1), repetitions):
                                        self.ui.textEdit.append('Channel: ' + str(channel) + '  Trace: ' + str(trace) + '  Rep: ' + str(rep))
                                        trace_count += 1
                                        # Trace Metadata
                                        trace_string += 'trace=' + str(trace_count) + '; '
                                        trace_string += 'catid=' + str(cat_count) + '; '
                                        trace_string += 'trialid=' + str(rep) + '; '
                                        trace_string += 'siteid=' + str(channel) + '; '
                                        trace_string += 'start_time=' + '0' + '; '
                                        trace_string += 'end_time=' + str(samples / h_file[key].attrs['samplerate_ad']) + '; '
                                        trace_string += '\n'

                                        if no_chan:
                                            raw_trace = h_file[key][test].value[trace - 1, rep - 1, :]
                                        else:
                                            raw_trace = h_file[key][test].value[trace - 1, rep - 1, channel - 1, :]
                                        # Add to Data File
                                        for sample in raw_trace:
                                            if sample >= self.chan_dict['channel_' + str(channel)]:
                                                stad.write(str(sample))
                                                stad.write(' ')
                                        stad.write('\n')
                                        meta_progress += trace_progress / float(repetitions)
                                        data_progress += trace_progress / float(repetitions)
                                        self.ui.progressBar_meta.setValue(meta_progress)
                                        self.ui.progressBar_data.setValue(data_progress)
                                        QtGui.qApp.processEvents()
                                else:
                                    stim_progress = trace_progress / stimuli_count[trace]
                                    for stim in islice(count(1), stimuli_count[trace]):
                                        self.ui.textEdit.append('Channel: ' + str(channel) + '  Trace: ' + str(trace) + '  Stim: ' + str(stim))
                                        cat_count += 1
                                        for rep in islice(count(1), repetitions):
                                            self.ui.textEdit.append('Channel: ' + str(channel) + '  Trace: ' + str(trace) + '  Stim: ' + str(stim) + '  Rep: ' + str(rep))
                                            trace_count += 1
                                            # Trace Metadata
                                            trace_string += 'trace=' + str(trace_count) + '; '
                                            trace_string += 'catid=' + str(cat_count) + '; '
                                            trace_string += 'trialid=' + str(rep) + '; '
                                            trace_string += 'siteid=' + str(channel) + '; '
                                            trace_string += 'start_time=' + '0' + '; '
                                            trace_string += 'end_time=' + str(stimulus['components'][stim-1]['duration']) + '; '
                                            trace_string += '\n'

                                            # h_file[key][test].value[trace, rep, chan, :]
                                            if no_chan:
                                                raw_trace = h_file[key][test].value[trace - 1, rep - 1, :]
                                            else:
                                                raw_trace = h_file[key][test].value[trace - 1, rep - 1, channel - 1, :]

                                            sample_start = stimulus['components'][stim-1]['start_s'] * h_file[key].attrs['samplerate_ad']
                                            sample_duration = stimulus['components'][stim-1]['duration'] * h_file[key].attrs['samplerate_ad']
                                            sample_end = sample_start + sample_duration
                                            stimuli_trace = raw_trace[:sample_end][sample_start:]
                                            # Add to Data File
                                            for sample in stimuli_trace:
                                                if sample >= self.chan_dict['channel_' + str(channel)]:
                                                    stad.write(str(sample))
                                                    stad.write(' ')
                                            stad.write('\n')
                                            meta_progress += stim_progress / float(repetitions)
                                            data_progress += stim_progress / float(repetitions)
                                            self.ui.progressBar_meta.setValue(meta_progress)
                                            self.ui.progressBar_data.setValue(data_progress)
                                            QtGui.qApp.processEvents()

                        # Build site string
                        # time_scale is 1 due to Sparkle storing time in seconds
                        for channel in islice(count(1), channels):
                            site_count += 1
                            site_string += 'site=' + str(site_count) + '; '
                            site_string += 'label=' + test
                            if channels > 1:
                                site_string += ' chan_' + str(channel) + '; '
                            else:
                                site_string += '; '
                            if h_file[key][test].attrs['mode'] == 'continuous':
                                site_string += 'recording_tag=continuous; '
                            elif h_file[key][test].attrs['mode'] == 'finite':
                                site_string += 'recording_tag=episodic; '
                            else:
                                # TODO Error
                                pass
                            site_string += 'time_scale=1; '
                            # TODO Calculate Time Resolution
                            site_string += 'time_resolution=0.001;\n'
                            meta_progress += 5 / float(channels)
                            self.ui.progressBar_meta.setValue(meta_progress)

        stam.write(site_string)
        stam.write('#\n')
        stam.write('# Category metadata\n')
        stam.write(category_string)
        stam.write('#\n')
        stam.write('# Trace metadata\n')
        stam.write(trace_string)

        stam.close()
        stad.close()
        self.ui.textEdit.append('\nComplete')

    def start(self):
        self.ui.progressBar_meta.reset()
        self.ui.progressBar_data.reset()

        self.convert()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    myapp = MainForm()
    myapp.show()
    sys.exit(app.exec_())