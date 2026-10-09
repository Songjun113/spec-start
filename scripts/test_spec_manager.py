import unittest,tempfile,json,hashlib
from pathlib import Path
import spec_manager as m
class Tests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
 def tearDown(self):self.tmp.cleanup()
 def fixture(self):
  m.init(self.root,'示例');r={'id':'r001','title':'完整交付','requirement':'完成用户要求的交付','source':'user request','required':True,'priority':0,'status':'in_progress','interpretation':{'state':'confirmed','statement':'验收完整交付'},'acceptance':[{'id':'a1','text':'真实产物检查','status':'pending','evidence':[]}],'depends_on':[]}
  data=json.loads((self.root/'spec/requirements.json').read_text());data['project']['scope_review']='confirmed';data['requirements']=[r];return data,r
 def store(self,data):(self.root/'spec/requirements.json').write_text(json.dumps(data),encoding='utf-8')
 def test_init_preserves_existing_and_is_idempotent(self):
  (self.root/'PROJECT.md').write_text('原项目记录');(self.root/'AGENTS.md').write_text('原项目约束');a=m.init(self.root,'test');self.assertFalse(a['recorded_completion_criteria_met']);before={str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()};m.init(self.root,'test');after={str(p.relative_to(self.root)):p.read_bytes() for p in self.root.rglob('*') if p.is_file()};self.assertEqual(before,after);self.assertIn('原项目记录',(self.root/'PROJECT.md').read_text());self.assertIn('原项目约束',(self.root/'AGENTS.md').read_text())
 def test_unfinished_goal_not_ready(self):
  d,r=self.fixture();self.store(d);self.assertFalse(m.refresh(self.root)['recorded_completion_criteria_met'])
 def test_verified_requires_evidence_and_confirmed_meaning(self):
  d,r=self.fixture();r['status']='verified';r['interpretation']['state']='ambiguous';r['acceptance'][0]['status']='verified';self.store(d);errors=m.check(self.root)[1];self.assertTrue(any('without evidence' in s for s in errors));self.assertTrue(any('unresolved' in s for s in errors))
 def test_done_failed_experiment_not_accepted(self):
  d,r=self.fixture();(self.root/'audit.json').write_text(json.dumps({'state':'DONE','passed':False}));r['status']='verified';r['acceptance'][0].update(status='verified',evidence=[{'path':'audit.json','kind':'audit','scope':'完整产物','check':{'field':'passed','equals':True}}]);self.store(d);self.assertTrue(any('condition failed' in s for s in m.check(self.root)[1]))
 def test_verified_evidence_then_hash_change(self):
  d,r=self.fixture();f=self.root/'audit.json';f.write_text('{"passed":true}');r['status']='verified';r['acceptance'][0].update(status='verified',evidence=[{'path':'audit.json','kind':'audit','scope':'完整产物','sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'check':{'field':'passed','equals':True}}]);self.store(d);result=m.refresh(self.root);self.assertTrue(result['recorded_completion_criteria_met']);self.assertFalse(result['semantic_completion_proven_by_tool']);f.write_text('{"passed":false}');self.assertTrue(any('changed evidence SHA' in s for s in m.check(self.root)[1]))
 def test_dependency_cycle_and_unknown_task_reference(self):
  d,r=self.fixture();other=json.loads(json.dumps(r));other['id']='r002';r['depends_on']=['r002'];other['depends_on']=['r001'];d['requirements'].append(other);self.store(d);(self.root/'spec/tasks.md').write_text('任务连接 r999');errors=m.check(self.root)[1];self.assertTrue(any('cycle' in s for s in errors));self.assertTrue(any('Unknown requirement links' in s for s in errors))
 def test_verified_cannot_skip_dependency(self):
  d,r=self.fixture();other=json.loads(json.dumps(r));other['id']='r002';other['status']='planned';d['requirements'].append(other);r['depends_on']=['r002'];r['status']='verified';self.store(d);self.assertTrue(any('before dependency' in s for s in m.check(self.root)[1]))
if __name__=='__main__':unittest.main()
