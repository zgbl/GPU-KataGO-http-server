// models/Registration.js
import mongoose from 'mongoose';

const registrationSchema = new mongoose.Schema({
  tournament: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'Tournament',
    required: true,
  },
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true,
  },
  status: {
    type: String,
    enum: ['已报名', '已付费', '已确认', '已取消'],
    default: '已报名',
  },
  registrationDate: {
    type: Date,
    default: Date.now,
  },
  // 可以添加其他相关字段，如付款信息、特殊要求等
});

const Registration = mongoose.models.Registration || mongoose.model('Registration', registrationSchema);

export default Registration;