#encoding: utf-8

from infosource_scraper.scrapers.scraper import Scraper
from infosource_scraper.models import InfoSource 
from main.models import DepartmentDataCategory,DataCategory,DataSet
from BeautifulSoup import  BeautifulSoup
import re
import urllib
import codecs

"""
    Given an URL, scrapes the list of information categories 
    specific to a department 
"""

class DepartmentSpecificCategoryScraper(Scraper):

    """
     maps page labels for data categories to model fields
    """
    LABELS_TO_MODELFIELDS = {
                       u'Record Number:': 'code', 
                       u'Description:': 'desc',
                       u'Format:': 'format',
                       u'Access:': 'access',
                       u'Document Types:': None }
    
    LABELS = LABELS_TO_MODELFIELDS.keys()
    
    """
    marks which of the labels can be spread over several lines
    """
    MULTILINE_ENABLED = {u'Description:': True,
                         u'Document Types:':True,
                         u'Access:': True,
                         u'Format:':True }
    
    def __init__(self, department, url):
        self.department = department
        super(DepartmentSpecificCategoryScraper,self).__init__(url) 
            
      
    def scrape(self):
        center = self.soup.find('div',{'class':'center'})
        data = unicode(center)
        
        # Pages from infosource.gc.ca are coded by hand in a haphazard way.
        # Just remove all the markup and work from that.

        #show the data before processing (for debugging)        
        f = codecs.open('./tmp/pre.txt','w','utf-8')
        f.write(data)
        f.close()

        # make sure all category labels have line breaks in the right place
        for label in self.LABELS:
            data = re.sub(u'<br /><strong><em>%s' %(label),u'<br />\n<strong><em>%s' %(label),data )
            data = re.sub(u'<br /><strong>%s' %(label),u'<br />\n<strong>%s' %(label),data )
            
        # get rid of microsoft characters 
        data = re.sub('\r','',data)      
        
        #combine multiple successive headers into a single line  
        data = re.sub('<p><strong>([^<]+?)<br />([^<]+?)</strong></p>','<p><strong>\g<1> \g<2></strong></p>',data)
        
        #strip HTML markup (it's easier)
        data = u''.join(BeautifulSoup(data).findAll(text=True))

        #show the data after processing (for debugging)
        f = codecs.open('./tmp/post.txt','w','utf-8')
        f.write(data)
        f.close()
 
        lines = data.split('\n')
        super_category_name = u''
        category_name = u''
        two_category_headers_in_a_row = False
        # basic single-mode parser
        multiline_mode = ''
        category_info = {}
        
        for line in lines:
            line_label,line_content = self._get_label(line)

            # is it really a record number?  Does it follow a format like a record number?
            # see 'http://infosource.gc.ca/inst/nrc/fed05-eng.asp', Urban Infrastructure
            # which has some mis-labeled information.
            
            # Assume a mis-labeled record number is really a document type.
            
            if line_label == u'Record Number:' and not self._matches_category_code_format(line):
                line_label = u'Document Types:'

            #print "---"+line + "---"
            if line_label:
                if self.MULTILINE_ENABLED.has_key(line_label):
                    multiline_mode = line_label
                    category_info[multiline_mode] = u''
                else:
                    multiline_mode = ''
                    

            #print "category:%s multiline:%s content:%s " % (line_category,multiline_mode,line_content)
            
            if multiline_mode != '':
                category_info[multiline_mode] += line_content
            else:
                # did we hit the end of a category description?
                if not line_label:
                    if len(category_info) != 0:
                        # flush the category info cache
                        if super_category_name and super_category_name != 'Institution-Specific Classes of Records':
                            category_name = super_category_name + u' - ' + category_name
                        self._save_category(category_name,category_info)
                        category_info = {}
                    if two_category_headers_in_a_row:
                        super_category_name = category_name
                    category_name = line_content
                    two_category_headers_in_a_row = True
                else:
                    two_category_headers_in_a_row = False
                    category_info[line_label] = line_content
                    
                    
    """
    given a line of text from the HTML file, check if it contains a 
    descriptive label.  
    
    returns: tuple(label (or none), rest of text line)
    """
    def _get_label(self,line):
        for label in self.LABELS:
            if re.search(label,line):
                content = re.sub(label,'',line)
                return((label,content))
        return( (None,line) )
    
    """
    does the passed information match the format for a category code
    as defined on infosource.gc.ca?
    """
    def _matches_category_code_format(self,line):
        if not re.search('\d',line):
            return( False )
        return( True )
                
    """
        save the information collected in the category info map as a new 
        information category in the database
    """            
    def _save_category(self,category_name, all_category_info):
        model_params = {'name':category_name,
                           'type':DataCategory.SPECIFIC}
        data_sets = u''
        for key in all_category_info.keys():
            if self.LABELS_TO_MODELFIELDS.has_key(key) and self.LABELS_TO_MODELFIELDS[key] != None:
                model_key = self.LABELS_TO_MODELFIELDS[key]
                model_params[model_key] = all_category_info[key]
            else:
                if key == 'Document Types:':
                    data_sets = all_category_info[key]
                else:
                    print "unknown category qualifier: %s" % key
        if data_sets == u'':
            data_sets = u'All Information'
        #print category_name
        #print str(model_params)
        try:

            if not DataCategory.objects.filter(code=model_params['code']):
                cat = DataCategory(**model_params).save()
             
            cat = DataCategory.objects.get(code=model_params['code'])
            DepartmentDataCategory.objects.get_or_create(dept=self.department,category=cat)

        except Exception, e:
            print(str(model_params))
            raise Exception("Error accessing category %s-%s: %s" % (self.department.name,category_name,str(e)))
        
        all_data_sets = self._all_data_sets(cat,data_sets)
        for (data_set_name,code) in all_data_sets:
                data_set_name = re.sub(u'.$',u'',data_set_name)
                data_set_name = re.sub(u';$',u'',data_set_name)
                #print "saving data set %s (%s)" % (data_set_name,str(code))
                set,g_or_c = DataSet.objects.get_or_create(category=cat,desc=data_set_name,code=code)
               
    """
        return a list of all data sets with their own ID numbers listed in 
        the 'Document Types' section.
        
        Returns a list of tuples (data_set_name, data_set_code)
        data_set_code may be null.
    """
    def _all_data_sets(self,category,data_sets):
        match = re.search(u'\s+(\S+)',category.code.strip())
        if not match:
              #print "couldn't find short code for: %s" % category.code
              return([[data_sets,None]])
        short_code = match.group(1)
        
        # does that code exist in our data set list followed by a number?
        match = re.search(short_code+'-\d+',data_sets)
        if not match:
            return([[data_sets,None]])
        
        try:
            multiple_data_sets = re.split(short_code+'-',data_sets)
        except Exception, e:
            print short_code
            print data_sets
            raise Exception( u'Error looking for short code %s in %s: %s' % (short_code, data_sets,str(e))  )
        
        if len(multiple_data_sets) == 1:
            #print "couldn't find short code %s in: %s (cat code=%s)" % (short_code,data_sets,category.code)
            return([[data_sets,None]])

        subsets = []

        for data_set in multiple_data_sets:
             match = re.search("\s*(\d+)\s+(\S+)",data_set)
             if match:
                print u'Found multiple data sets for %s %s-%s'%(self.department.name,match.group(2),match.group(1))
                subsets.append( [match.group(2),match.group(1) ] )
             else:
                 if len(data_set.strip()) != 0:
                     s =  "Error parsing data set segment %s, part %s (%s)" % (data_sets,data_set,short_code)
                     raise Exception(s)
        return(subsets)

class DepartmentStandardCategoryScraper(Scraper):

    """ 
        Map of common standard category name errors
    """
    COMMON_ERRORS = { u'Account and Accounting':u'Accounts and Accounting',
                      u'Access to Information and Privacy Request':'Access to Information and Privacy Requests',
                      u'Administration and Management Systems':u'Administration and Management Services', 
                      u'Administrative and Management Services':u'Administration and Management Services',
                      u'Audit':u'Audits',
                      u'Automated Document, Records and Information Management Systems':
                      u'Automated Document, Records, and Information Management Systems',
                      u'Automated Document Records and Information Management Systems':
                      u'Automated Document, Records, and Information Management Systems',
                      u'Automated Document Records and Information Management System':
                      u'Automated Document, Records, and Information Management Systems',
                      u'Automated Document, Records and Information Management System':
                      u'Automated Document, Records, and Information Management Systems',
                      u'Automated Document, Records, Information Management Systems':
                      u'Automated Document, Records, and Information Management Systems',
                      u'Business Continuity Plans':'Business Continuity Planning',
                      u'Boards, Committee and Councils':u'Boards, Committees and Councils',
                      u'Co‑operation and Liaison': #here, the dash is in UTF-8
                      u'Co-operation and Liaison',
                      u'Cooperation and Liaison':u'Co-operation and Liaison',
                      u'Communictions':'Communications',
                      u'Classifications of Positions':'Classification of Positions',
                      u'Building and Properties':u'Buildings and Properties',
                      # OMG!
#                      u'Disclosure to Investigate Bodies':u'Disclosure to Investigative Bodies',
                      u'Employment and Staffing':u'Recruitment and Staffing',
                      u'Equipment and supplies':u'Equipment and Supplies',
                      u'Equipement and Supplies':u'Equipment and Supplies',
                      u'Furniture and Furnishing':u'Furniture and Furnishings',
                      u'Recruitmnet and Staffing':u'Recruitment and Staffing',
                      u'Recruitmnet and Staffing:':u'Recruitment and Staffing',
                      u'Salary and Wages':u'Salaries and Wages',
                      u'Occupational Health, Safety':u'Occupational Health and Safety',
                      u'Occupational Health, Safety and Welfare':u'Occupational Health and Safety',
                      u'Procurement':u'Procurement and Contracting',
                      u'Pension and Insurance':u'Pensions and Insurance', 
                      u'Training and Devlopment':u'Training and Development',
                      }
    
    def __init__(self,department,url):
        self.department = department
        super(DepartmentStandardCategoryScraper,self).__init__(url) 
    
    def scrape(self):
        center = self.soup.find('div',{'class':'center'})
        paras = center.findAll('p')
        for para in paras:
            para = re.sub(u'\s+',u' ', para.contents[0].strip())
            category_name = self._fix_common_errors(unicode(para))
            if category_name.count('Please see') == 0:
                category = DataCategory.objects.filter(name=category_name)[:1]
                if category:
                    DepartmentDataCategory.objects.get_or_create(dept=self.department,category=category[0])
                else:
                    f = codecs.open('./data/' + self.department.abbrev + '-standard.txt','w','utf-8')
                    f.write(category_name)
                    f.close()
                    print u"Department %s listed having a standard data set called '%s', which is not defined in the list of standard categories" % (self.department.name,category_name)
          
    def _fix_common_errors(self,category_name):
        if self.COMMON_ERRORS.has_key(category_name):
            return self.COMMON_ERRORS[category_name]
        return( category_name )
      
class DepartmentScraper(Scraper):
    
    def __init__(self, department):
        self.department = department
        self.infosource = InfoSource()
        url = self.infosource.department_index(department)
        return( super(DepartmentScraper,self).__init__(url )) 
    
    """
        return the link to the institution-specific list of data categories
        for this department.
    """    
    def institution_data_page(self):
        link_text = self.soup.find(text=re.compile("Institution-Specific Classes of Records"))
        if link_text:
            link = link_text.findParent('a')
            return(self.infosource.department_page(self.department,link['href']))
        else:
            return( None ) 
        
    """ 
        return the link to the standard list of data categories for this 
        department.
    """
    def standard_data_page(self):
        link_text = self.soup.find(text=re.compile("Standard Classes of Records"))
        if link_text:
            link = link_text.findParent('a')
            return( self.infosource.department_page(self.department,link['href']))
        else:
            print "All departments should have a standard classes of record.  None found on %s." % (self.cache.path)
            return( None )
        
    def scrape(self):
        print "scraping department " + self.department.name
        to_scrape = { self.standard_data_page() : DepartmentStandardCategoryScraper,
                      self.institution_data_page() : DepartmentSpecificCategoryScraper
                     }

        for page, scraper_class in to_scrape.items():
            if page:
                scraper = scraper_class(self.department,page)
                scraper.scrape()
        