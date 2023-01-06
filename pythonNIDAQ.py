class nidaqmxWrappers:

    def __init__(self):

        print('welcome to nidaqmxWrapper class')

        self.buildNIDAQmxModule()
        self.buildSystem()


    def buildSystem(self):

        import nidaqmx.system
        system = nidaqmx.system.System.local()

        self.system = system


    def buildNIDAQmxModule(self):

        import nidaqmx
        self.nidaqmx = nidaqmx

        print(' ')
        print('NIDAQmx module imported, use self.nidaqmx to access it')
        print(' ')

    def printDevices(self):

        system = self.system

        for device in system.devices:

            print(device)


    def printDeviceName(self):

        system = self.system

        for device in system.devices:

            print(device)

            
            # here we are printing analog inputs (ai) phyiscal channels

            for physChannel in device.ai_physical_chans:

                print(physChannel.name)
                print(type(physChannel.name))

            # here we are printing analog inputs (ai) phyiscal channels

            for physChannel in device.ao_physical_chans:

                print(physChannel.name)
                print(type(physChannel.name))


    def returnTaskObj(self):

        nidaqmx = self.nidaqmx

        taskObj = nidaqmx.Task()

        return taskObj

    def getTaskNames(self):

        nidaqmx = self.nidaqmx

        taskPropertyObj = nidaqmx.system._collections.persisted_task_collection.PersistedTaskCollection.task_names

        taskNames = taskPropertyObj.__get__(taskPropertyObj)

        return taskNames


    def getTaskObjects(self):

        nidaqmx = self.nidaqmx

        system = self.system

        taskObj = system.tasks

        return taskObj


        



class test:

    def __init__(self):

        print('welcome to the test class')

        print(' ')
        print('to get nidaqObj, use:')
        print('nidaqObj = testObj.getNidaqObj()')




    def testPrintDevices(self):

        print(' ')

        import pythonNIDAQ
        from pythonNIDAQ import nidaqmxWrappers

        nidaqObj = nidaqmxWrappers()

        nidaqObj.buildSystem()
        nidaqObj.printDevices()

        print('test complete')

        print(' ')

    def testPrintDeviceName(self):

        print(' ')

        import pythonNIDAQ
        from pythonNIDAQ import nidaqmxWrappers

        nidaqObj = nidaqmxWrappers()

        nidaqObj.buildSystem()
        nidaqObj.printDeviceName()

        print('test complete')

        print(' ')

    def getNidaqObj(self):

        from importlib import reload

        import pythonNIDAQ
        reload(pythonNIDAQ)
        from pythonNIDAQ import nidaqmxWrappers

        nidaqObj = nidaqmxWrappers()

        return nidaqObj


    def testTask(self):

        nidaqObj = self.getNidaqObj()

        nidaqObj.buildSystem()

        taskObj = nidaqObj.returnTaskObj()

        print(type(taskObj))
        print(taskObj)

        taskObj.ai_channels.add_ai_thrmstr_chan_vex('tempSensor1/ai7')
        reading = taskObj.read()

        print('first read')
        print(reading)

        print(' ')
        print('next we use the task obj to read readings 100x')

        # the readings before were okay! but i didn't print out the outputs
        for i in range(100):
            reading = taskObj.read()
            print(reading)
            print(type(reading))

        taskObj.close()

        #taskObj.ai_channels.add_ai_thrmstr_chan_vex('tempSensor1/ai6')
        #taskObj.read()

    def testReadExistingTask(self):

        nidaqObj = self.getNidaqObj()

        taskNames = nidaqObj.getTaskNames()

        print(taskNames)

        # here we read the names of the persisted tasks

        taskObjList = nidaqObj.getTaskObjects()

        for persistedTask in taskObjList:

            # we need to load the persisted task first before we read

            #task = persistedTask.load()
            
            # we can't load it... because it conflicts with existing task name
            # you usually need to close NI max in order to use this properly
            #task.read()

            print(persistedTask)

            task = persistedTask.load()

            print(task.name)

            # the following part is manual, you have to set it properly in nimax

            if task.name == 'MyTemperatureTask':
                #task.start()
                taskValue = task.read()
                print(type(taskValue))
                print(taskValue)

            if task.name == 'moduleATemperatureReading':
                #task.start()
                taskValue = task.read()
                print(type(taskValue))
                print(taskValue)


            task.close()

            # note that task objects MUST be closed properly everytime
            # otherwise we will get errors
            # then we will either need to use the reset_device()
            # or restart python
            # in order to clear the memory properly

        print('task read list complete')


        print('now we are reading the existing tasks and reading them manually')
        print(' ')
        print(' ')

        
        persistedTask = taskObjList[1]

        task = persistedTask.load()

        print(task)
        task.start()
        a = task.read()
        print(type(a))
        print(a)
        task.close()

        # i can't load persisted tasks...
        #task = persistedTask.load()
        #task.read()

        import nidaqmx

        #inStream = nidaqmx.task.InStream()

        # we read our persisted tasks :) 



class workspace:

    def __init__(self):

        print('initialising workspace')

        self.initialiseDefaults()


    def getTestObj(self):

        self.reloadClasses()
        self.testObj = self.test()

        return self.testObj

    def getNidaqmxWrappersObj(self):

        self.reloadClasses()
        self.nidaqmxWrappersObj = self.nidaqmxWrappers()

        return self.nidaqmxWrappersObj



    def initialiseDefaults(self):

        import pythonNIDAQ

        from pythonNIDAQ import nidaqmxWrappers
        from pythonNIDAQ import test

        self.nidaqmxWrappers = nidaqmxWrappers
        self.test = test

        from importlib import reload
        self.reload = reload

        print("workspace defaults initiated")

    def reloadClasses(self):

        reload = self.reload

        import pythonNIDAQ
        reload(pythonNIDAQ)


        from pythonNIDAQ import nidaqmxWrappers
        from pythonNIDAQ import test

        self.nidaqmxWrappers = nidaqmxWrappers
        self.test = test


def printHelp():

    print('hello, welcome to the pythonDAQmxWrapper module')

    print(' ')

    print('to load test modules use:')

    print(' ')

    print('import pythonNIDAQ')
    print('self = pythonNIDAQ.workspace()')

    print(' ')
    print('testObj = self.getTestObj()')

    print(' ')
    print('to load the nidaqmxWrappers object use:')

    print('nidaqmxWrapperObj = self.getNidaqmxWrappersObj()')


printHelp()